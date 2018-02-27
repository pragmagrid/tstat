#! /usr/bin/perl
#==============================================================================
# tstat_rrd.cgi	-*- v2.1 -*- Wed Jun  8 18:44:35 CEST 2005 -*- Dario Rossi
#------------------------------------------------------------------------------
# url parameters:
# dir=	       	the directory where the rrd files are (i.e., a specific trace)
# var=         	one of Tstat parameters (e.g., rtt_avg_in, ip_len_in, ...)
# template=    	one of (avg|stdev|idx|prc|hit), developed by applyTemplate() below
# duration=    	temporal window size (until end of samples)
# logscale=    	flag; toggle logscale
# agg=		flag; toggle wether to aggregate in/out and c2s/s2c flows
# bigpic=      	flag; doubles the picture size
# advopt=      	flag; toggle other options, such as:
# describe=	flag; toggle description
#   advcmd=	flag; toggle wether to plot picture or dump RRDtool command
#   yauto=     	flag; whether to use autoscaling
#   in=      	minimum yscale value
#   ymax=      	maximum yscale value
# format=	(png*|eps|pdf|rrd) used for creating download links
#
#	NOTE: $RRD_DATA/url_param("dir")/url_param("var").rrd
#	should be an existent file; the script enforce this check
#	by automatically selecting the available templates and
#	neglecting the one that whould cause an error
#
#
# other parameters:
#       every rrd directory may contain a HEADER, a FOOTER and a README
#       files, allowing custom informations to be naturally embedded in
#       each of the traces ``main page'' (i.e., when no parameter has been
#       chosen yet).
#       By default, the cgi tries to load the html version (thus,
#       FILE.html); otherwise, tries to displays "<pre> `cat FILE` </pre>" 
#       if such a file exists; finally, it will display a default message
#       held in $default{README} hardcoded in the script
#
# internal cgi configuration:
# 	see the configuration section below
#
# maintenance:
#	this has gone quite complex... for extensions, look for #NEWVAR 
#	comments below


#   ____________________________  
#  /				\ 
# /    libraries      __________/ 
# \__________________/.:nonsns:.  
# 				  
# makes things work when run without install
#	use lib qw( ../perl-shared/blib/lib ../perl-shared/blib/arch );
# this is after RRDtool `make install`... check your directory settings
# 
use lib qw( /usr/local/rrdtool/lib/perl);

use RRDs;
use Date::Manip;
use Data::Dumper;
use CGI qw/:standard/;
use CGI::Carp qw(fatalsToBrowser set_message carp);
use Time::localtime;

BEGIN {
   sub handle_errors {
      my $msg = "@_";
      print "<h1>Oh gosh</h1>";
      print "<p>tstat_rrd.cgi got an error:  <br><pre>$msg</pre></p>";
  }
  set_message(\&handle_errors);
}


#   ____________________________  
#  /				\ 
# /    configuration  __________/ 
# \__________________/.:nonsns:.  
# 				  
$debug=0;
$standalone_html = 1;  # add <html><body> ... </body></html>

#
# tstat_rrd output configuration: parameter separator 
# depends on tstat's RRD_TREE compilation option
# may be '/' if param/prc90.rrd, by default is param.prc90.rrd
$RRD_TREE = '.'; 

# specify path to the root of the rrd database tree
# by default, I assume there is a symbolic link in cgi-bin/ 
# named rrd_data
$RRD_DATA = 'rrd_data'; 

$RRD_GALLERY = 'rrd_gallery'; 

# same thing for image directory
# in my case, var/www/cgi-bin/rrd_images is
# a symbolic link to "/var/www/html/rrd_images"; 
# from the html browser's perspective
$IMG_DIR = "rrd_images"; 


# starting from v2.5, you have two differenent timescales
@RRD_TIME_LO  =  qw(12h 3d 1w  1m  1y);
@RRD_TIME_HI  =  qw(1h  4h 12h 24h 48h);
@RRD_TIME = @RRD_TIME_LO;


%tstat_css = (
  '<h1>' => '<H1>',
  '<h2>' => '<H2>',
);
%eurongi_css = (
  '<h1>' => '<H1 class="rouge">',
  '<h2>' => '<H2 class="noir">',
  '<h3>' => '<H3 class="noir">',
  '<a '  => '<span class="rouge:hover"><a ',
  '</a>' => '</a></span>',
  '<b>'  => '<span class="rouge"><b>',
  '</b>' => '</b></span>',
);  

%default = (
   HEADER => '',
   FOOTER => 'Tstat/RRD Web Interface (Dario Rossi)',	
   README => <<END,
<hr>
<h3> CGI interface </h3>
The CGI interface has been designed to quickly respond
to your actions, meaning that the dropdown menus and
the checkbuttons automatically trigger plot changes.
<ul>
<li> Two dropdown menus allow to select the <B>trace</b>
and the <b>variable</b> to observe.
<li> The two buttons <b> start over</b> and <b> home</b>
bring the user up a level or to the root of the
Round Robin Database; optionally, you can directly
browse and download the <b> RRData</b>
<li> Different options allows the user to, e.g., read the 
<b>description</b> of the metric and templates, or
toggle the use of <B>bigger pictures</b>, or allow to
select different <b>time windows</b> for short traces
processed with a higher sampling rate.
<li> An interesting feature allow to <b>aggregate</b> in 
a single plot several directions: specifically, outgoing (top,+)
incoming (bottom,-) flows will be aggregated together as well
as client-2-server (top,+) and server-2-client (bottom,-)
flows.
<li> The <b>advanced...</b> checkbox gives the user the opportunity
of finely tuning the y-axis scale (e.g., <b>autoscaling</b>,
<b>logscale</b>), or plot the RRDtool command used to produce 
the plot.
<li> Finally, you can select among the available <b>templates</b> and
<b>timespans</b>.
</ul>

Have a good Tstat!
END
);

=pod
<hr>
<h3> Navigation Instructions </h3>
<ul>
	<li> To	inspect traffic that has different <i>geographical</i>
	and <i>temporal</i> properties you can browse through different
	<b>traces</b>, 
	</li>
	
	<li> You may then select one of the different <b>parameters</b>, to
	gather significative insights on the <i>statistical properties</i> of
	the traffic. </li>

	<li> Several <b>templates</b> allow to browse through different 
	visual <i>presentation</i> of the same statistical dataset
	<ul>
	<li>
	moreover, the same template can be applied to different temporal views.
	</li>
	</ul>
	</li>
	
	<li> Several <b>temporal views</b> allow to observe complex traffic
	pattern at different <i>time granularity</i> 
	<ul>
	</ul>
	</li>
	
	<li>
	Besides, you can <b>finely tune</b> several properties of the graph, 
	such as the size of the graph, wether to use logarithmic scales,  or the
	y-axis scale, ...
	</li>
	<li>
	Finally, the <b>start over</b> button will bring you to the main page of
	each separate trace, whereas the <b>home</b> button will bring you to
	the main page common to all the traces.
	</li>

</ul>
=cut

# sub scaleDuration {
# my $scale = shift;
#    $RRD_TIMEh *= $scale;
#    $RRD_TIMEd *= $scale;
#    $RRD_TIMEw *= $scale;
#    $RRD_TIMEm *= $scale;
#    $RRD_TIMEy *= $scale;
# }
# sub shiftDuration {
# my $shift = shift;
#    $RRD_TIMEh += $shift;
#    $RRD_TIMEd += $shift;
#    $RRD_TIMEw += $shift;
#    $RRD_TIMEm += $shift;
#    $RRD_TIMEy += $shift;
# }
# 

#NEWVAR	    
# global parameters have the form ``$pXxx''
use vars qw($tstat_rrd_cgi 
	$pLog $pTpl $pLen $pDir $pReadme $pHeader $pFooter $pStyle 
        $pBigpic $pAggpic $pAdvcmd $pLogscale $pDescribe
	$pFormat %pFormat $pHifreq $pExclude $pInclude %pExclude %pInclude
	$pNEWVAR );

use vars qw(%pVar $pVar @pVar %pVarAttr $jsMenuVar); 
	# for splitvar

use vars qw(%pAdirectional %pServerifiable 
	%pDirection $pDirection @pDirection %pDirectionAttr $jsMenuDirection); 
	# for splitdirection
	
use vars qw($jsAddToGallery);
#NEWVAR	    

sub extremeDebug {
my $dbg = {};
    map { 
      m/^([%@\$])(.+)$/g;
      $kind = $1;
      $name = $2;
      eval "\$dbg->{$name} = \\$kind\{ $_ \}";
      #die "\$dbg->{$name} = $kind\{ $_ \}";
    }   qw($tstat_rrd_cgi 
	$pLog $pTpl $pLen $pDir $pReadme $pHeader $pFooter $pStyle 
        $pBigpic $pAggpic $pAdvcmd $pLogscale $pDescribe
	$pFormat %pFormat $pHifreq $pExclude $pInclude %pExclude %pInclude
	$pNEWVAR
	%pVar $pVar @pVar %pVarAttr $jsMenuVar
	%pAdirectional %pServerifiable 
	%pDirection $pDirection @pDirection %pDirectionAttr $jsMenuDirection);
die Data::Dumper->Dump( [ \@_, $dbg ], [ 'ARGS', 'you_left_me_with_no_choice' ] );
}


# global data
use vars qw($idx2value %description2param %description @defColor $color %css); 


sub hidden_stuff {
    return remote_host() !~ m/(polito.it$|^130\.192\.|^192\.168\.)/
}     
	    
$tstat_rrd_cgi = (split '/', $0)[-1]; #"tstat_rrd.cgi";

#   ____________________________  
#  /				\ 
# /    main           __________/ 
# \__________________/.:nonsns:.  
# 				  
#
# we will call main() at the end of file, after all global vars are defined
#
sub main {
    $menu=1; #GCI output by default
    if (url_param()) {	     
	     if( url_param('gallery_show') ) {
	     	  gallery_show();
	     }
	     if( url_param('gallery_save') ) {
	     	  gallery_save( url_param('gallery_save'), 
		  		url_param('gallery_add'), 
				url_param('gallery_cmd') );
	     }
	     
    	     if( url_param('gallery_add') ) {
	          gallery_add( 	url_param('gallery_add'), 
		  		url_param('gallery_cmd') );
	     }
    
    
	     $pLog = url_param('logscale');
             $pTpl = url_param('template');
             $pLen = url_param('duration');	     
             $pBigpic = url_param('bigpic') || 'true';
             $pAdvopt = url_param('advopt');	     
  	          $pAdvopt ||= 'true';     
             $pAdvcmd = url_param('advcmd');	     
	     ########			     
	     #    $pAggpic = url_param('aggpic');	
  	     #     $pAggpic ||= 'false';     
	     $pDirection = url_param('direction');	     
	     #$pDirection = 'both' if $pDirection eq '';
	     ########
	     $pAutoconf = url_param('yauto');	     
	     $pYmin = url_param('ymin');	     
	     $pYmax = url_param('ymax');	     
	     $pFormat = url_param('format');
   	     $pHifreq = url_param('hifreq');	     
	     $pHifreq ||=  'false';
	     @RRD_TIME = ($pHifreq eq 'true') ? @RRD_TIME_HI : @RRD_TIME_LO;

	     #NEWVAR	     
		 $pDescribe = url_param('describe');	     
		 #$pNewvar = url_param('newvar');	     
	     #NEWVAR

             $pExclude = defined(url_param('exclude'))? url_param('exclude') : '';
             my @list = split ',',$pExclude;
             foreach $item (@list)
              {
                $pExclude{$item} = 1;
              }
             $pInclude = defined(url_param('include'))? url_param('include') : '';
             @list = split ',',$pInclude;
             foreach $item (@list)
              {
                $pInclude{$item} = 1;
              }

             $pDir = url_param('dir') || $RRD_DATA;
	     $pDir = "$RRD_DATA/$pDir" unless $pDir =~ $RRD_DATA;

             $pVar  = url_param('var') || 'NULL'; 
	     
	     # used for first time in dir $pDir
	     $pReadme =  ( -e "$pDir/README.html" ) ?
		 	    join(" ", "<hr>",`cat $pDir/README.html`) :
 			 ( -e "$pDir/README" ) ?
		 	    join(" ","<hr><pre>",`cat $pDir/README`,"</pre>") : "";
	     $pReadme .= $default{README};                 				

             $pFooter = "";
	     $pHeader = ""; 
	     $pStyle = url_param('style') ne '' ? 'EuroNGI' : 'home';
	     if ($pStyle eq 'EuroNGI') {
      	         $pCSS = '<LINK href="eurongi.css" rel=stylesheet>';	     
	     	 %css = %eurongi_css; 
		 $pHeader .= "<font size=-2>";
		 $pFooter .= "</font>";
             } else {
      	         $pCSS = 
                "<STYLE type='text/css'>
                        body {  font-family: Arial, sans-serif; }
                        h1, h2, h3, h4, h5, h6 {  font-family: Verdana, sans-serif, bold; }
                        p {   padding-left: 3em; }
                        div.tooltip {
                            background-color: #ffffbb;
                            border: solid 1px orange;
                            font-size: 9pt;
                            display: block;
                            position: absolute;
                            padding:1pt 1pt;
                        }
                </STYLE>";	     		 
	     	 %css = %tstat_css; 
             }		 
	     $pHeader .= ( -e "$RRD_DATA/HEADER.html" )  ?
	 		    join(" ",`cat $pDir/HEADER.html`) :
 			( -e "$pDir/HEADER" ) ?
		 	    join(" ","<hr><pre>",`cat $pDir/HEADER`,"</pre>") : "";
	     $pFooter .= ( -e "$RRD_DATA/FOOTER.html" )  ?
	 		    join(" ",`cat $RRD_DATA/FOOTER.html`) :
                	    "<hr>";
 
  
	     # scaleDuration(param('timescale')) if param('timescale');
	     # shiftDuration(param('timeshift')) if param('timeshift');
	     # resetDuration() if param('timereset');
    } 

    $pLen =~ s/(\d+)w$/$1wk/;
    print menuHtml();
}

#   ____________________________  
#  /				\ 
# /    returnHtml     __________/ 
# \__________________/.:nonsns:.  
# 				  
 
sub returnHtml { 
  # my $ppp = join "\n", map { "$_ = " . url_param($_) . "<br>\n" } url_param();
  #my $ppp="";
  
   my $html = "$pCSS $pHeader\n@_\n$pFooter";
   map {
       $html =~ s/$_/$css{$_}/sig;
   } keys %css;
#   return ( $standalone_html ) ? 
#	    join(" ", header, start_html("$0"), $html) :
#	    $html;
   return ( $standalone_html ) ? 
	    join(" ", header, 
		start_html(-title=>"Tstat Web Interface", 
                           -script=>{-language=>'JAVASCRIPT', -src=>'/javascript/tooltip.js'}
		), $html) : 
		$html;
}


sub verb { print STDERR ("@_\n") if $debug };
#sub verb { CGI::Carp::confess("@_\n") if $debug };


#   ____________________________  
#  /				\ 
# /    filter         __________/ 
# \__________________/.:nonsns:.  
# 				  
# filter out unwanted components
#
sub is_valid {
  my ($trace,$param) = @_;
  # no need for local flows in Polito or GARR traces
  return 0 if ($trace =~ m/(Polito|GARR)/) && $param =~ m/_loc$/;  
  return 0 if $trace =~ m/^test/ && hidden_stuff();    
  return 1;
}


# look for statistical rrd parameters in directory
# passed as argument.
sub dir2var {
my $dir = shift;
my $rrd = "$dir/*rrd";

   #possibly have to quote if dir contains spaces	
   my @par = glob (($rrd =~ m/\s/ ) ? "'$rrd'" : $rrd);
   map { 
     $_ = (split '\.', (split '/', $_)[-1])[0];
     
#splitdirection     
     s/_(in|out|loc|c2s|s2c)//;
   } @par;

   undef %uniq;   
   @uniq{@par} = ();
   undef @keys;   
   map {
   	push @keys, $_ if( $description{$_} ne "" ) && is_valid($dir,$_);
   } keys %uniq;
   return sort { $description{$a} cmp $description{$b} } @keys;  # remove sort if undesired
}   

sub have_rrd {
    my @ret;
    foreach $tag (@_) {
      @glob = glob("$pDir/$pVar$tag*rrd");
      push @ret, @glob if @glob;
    }  
    return @ret;
}



#   ____________________________  
#  /				\ 
# /    formHtml       __________/ 
# \__________________/.:nonsns:.  
# 				  
#
#  generate form to apply templates and browse through dirs
#  this is the core of the human-interface: everything is a
#  mix of CGI, javascript and html references. Good luck if 
#  you wish to modify it... in this case, adding a flag should
#  be still relatively easy.
# 
sub formHtml {
   #
   # available traces in RRD_DATA
   #
   my (@pDir, %pDir, $long, $short);
#   open FIND_DIR, "find $RRD_DATA/ -type d | sort |";
   open FIND_DIR, "find $RRD_DATA/  | sort |";
   while (<FIND_DIR>) { 
     chomp; 
     if( @glob = glob("$_/*.rrd") ) {
        ### $f .= "$_ : @glob";
	$long = $_;
	s/^.*$RRD_DATA\///g;    
	$short = $_;
	push @pDir, $_ if  (!m/^\s+$/ && is_valid($_));
	$pDir{$short} ||= "$short";
     }	else {
     	$f .= "Dir $_ do not glob";
     }
   }   
   close FIND_DIR;
   
   ( $pDir_default = $pDir ) =~  s/^.*$RRD_DATA\///g;    
   @pDir = sort { $a cmp $b } @pDir;	   
   if( $pDir eq $RRD_DATA ) {
  	$pDir{$RRD_DATA}='--Select a trace--';
	unshift @pDir, $RRD_DATA;
   }  

   
#===============================================
# available vars in pDir
#-----------------------------------------------
   undef %pVar;
   @pVar = dir2var( $pDir );
   #map { $pVar{$_} = "<font size=-2> $description{$_} </font>" } @pVar;
   map { $pVar{$_} = "$description{$_}" } @pVar;

   undef %pVarAttr;
#   my %pDirAttr, %class = ( style=>"{ font-family : sans-serif; font-size : 10px; }" );
   my %pDirAttr;
   my %class = ( style=>"font-family : sans-serif;" );
   map { $pVarAttr{$_} = \%class; } @pVar;
   map { $pDirAttr{$_} = \%class; } @pDir;

   if( $pVar eq 'NULL' ) {
  	$pVar{'NULL'}='--Select a parameter--';
	unshift @pVar, 'NULL';
   } 

#===============================================
#  split direction
#-----------------------------------------------

   split_direction_failback();

   
#NEWVAR
   $js{"XXX"} = "";
   $js{loc} = "$tstat_rrd_cgi?";
   $js{loc}.="duration=$pLen&" if $pLen; 
   $js{loc}.="template=$pTpl&" unless $pLen;
   $js{dir} = "dir=$pDir&";
   $js{log} = "logscale=$pLog&";
   $js{big} = "bigpic=$pBigpic&";
   $js{var} = "var=$pVar&";
   ######
   # $js{agg} = "aggpic=$pAggpic&";
   #$js{agg} = "direction=$pDirection&";
   $js{agg}="direction=$pDirection&" unless ($pDirection eq 'NULL') || ($pDirection eq 'NONE');
   ######
   $js{des} = "describe=$pDescribe&";

   $pYmax = $pYmin='' if( $pAutofconf eq 'true');
   $js{cmd} = "advcmd=$pAdvcmd&";
   $js{adv} = "advopt=$pAdvopt&";
   $js{ymn} = "ymin=$pYmin&"   if $pAdvopt && ($pAutoconf eq 'false') && $pYmin ne '';
   $js{ymx} = "ymax=$pYmax&"   if $pAdvopt && ($pAutoconf eq 'false') && $pYmax ne '';;
   $js{yac} = "yauto=$pAutoconf&";
   $js{yA1} = "yauto=true&"; #when the template changes, set autoconf
   $js{yA0} = "yauto=false&"; #when the template changes, set autoconf
   $js{hif} = "hifreq=$pHifreq&";

   $js{exc} = "exclude=$pExclude&";
   $js{inc} = "include=$pInclude&";
#
# add a new parameter to the url
# 	 $js{NEW} = "newvar=$pNewvar&";

   $jsMenuBtn ="location.href=\"$tstat_rrd_cgi?$js{dir}var=NULL\"";
   $jsHomeBtn ="location.href=\"$tstat_rrd_cgi?var=NULL&dir=$RRD_DATA\"";
   $jsMenuVar ="location.href=\"$js{loc}$js{XXX}$js{XXX}$js{XXX}$js{dir}$js{log}$js{big}$js{adv}$js{yA1}$js{XXX}$js{XXX}$js{agg}$js{cmd}$js{des}$js{hif}var=\"+this.options[this.selectedIndex].value;";
   $jsMenuDir ="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{XXX}$js{log}$js{big}$js{adv}$js{yac}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}dir=\"+this.options[this.selectedIndex].value;";
   $jsCheckLog="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{XXX}$js{big}$js{adv}$js{yac}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}logscale=\"+document.forms.tstatForm['tstatCheckLog'].checked;";
   $jsCheckBig="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{XXX}$js{adv}$js{yac}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}bigpic=\"+document.forms.tstatForm['tstatCheckBig'].checked;";
   $jsCheckAdv="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{XXX}$js{yac}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}advopt=\"+document.forms.tstatForm['tstatCheckAdv'].checked;";
   $jsAutoconf="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{XXX}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}yauto=\"+document.forms.tstatForm['tstatAutoconf'].checked;";
   $jsYmin    ="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{XXX}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}ymin=\"+document.forms.tstatForm['tstatYmin'].value;";
   $jsYmax    ="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{XXX}$js{agg}$js{cmd}$js{des}$js{hif}ymax=\"+document.forms.tstatForm['tstatYmax'].value;";
 ########			     
 #  $jsCheckAgg="location.href=\"$js{loc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{XXX}$js{cmd}$js{des}$js{hif}aggpic=\"+document.forms.tstatForm['tstatCheckAgg'].checked;";
  $jsDirection="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{XXX}$js{cmd}$js{des}$js{hif}direction=\"+this.options[this.selectedIndex].value;";
 ########
   $jsCheckCmd="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{agg}$js{XXX}$js{des}$js{hif}advcmd=\"+document.forms.tstatForm['tstatCheckCmd'].checked;";
   $jsCheckDes="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{XXX}$js{hif}describe=\"+document.forms.tstatForm['tstatCheckDes'].checked;";
   $jsCheckHif="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{XXX}hifreq=\"+document.forms.tstatForm['tstatCheckHif'].checked;";
   
   map {
      $pFormat{$_} ="location.href=\"$js{loc}$js{exc}$js{inc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{agg}$js{cmd}$js{des}$js{hif}format=$_";	     
   } qw(eps pdf rrd);   
#
# javascript to execute -onClik when the NEW's Checkbox state is toggled. 
# note that js{NEW} has to be added to ALL the other javascripts BUT this
# one (where you should use $js{XXX} instead for visual padding)
#
#  $jsCheckNEW="location.href=\"$js{loc}$js{var}$js{dir}$js{log}$js{big}$js{adv}$js{yA0}$js{ymn}$js{ymx}$js{agg}$js{XXX}newvar=\"+document.forms.tstatForm['tstatCheckNew'].checked;";
#
#NEWVAR



   
   ### (Dumper( [ $pDir_default, \@pDir, \%pDir ] )); #"3) pDir=$pDir pDirVEC @pDir pDirHASH %pDir");
    my $timeSpan = "";
    if( $pDir ) {
      my $tspanFile = (glob("$pDir/*rrd"))[0];
      if ( $tspanFile ) {        
          ####RRD BUG
	  my $first = ParseDateString("epoch @{[RRDs::first('--rraindex' ,'3', $tspanFile)]}");
	  #### my $first = ParseDateString("epoch @{[RRDs::first($tspanFile)]}");
	  ####RRD 
	  my $last  = ParseDateString("epoch @{[RRDs::last($tspanFile)]}");
	  my $start = UnixDate($first,'%A the %E of %B %Y, at %H:%M ');
	  my $end   = UnixDate($last,'%A the %E of %B %Y, at %H:%M');
	  my $err;
          # YY:MM:WK:DD:HH:MM:SS  the years, months, etc. between
	  my @unit = qw(year month week day hour minute second);
	  my ($offset,$length) = (0,"");	  
          map { 
	     s/^\+//g;
	     $length .= $_>1 ? "$_ $unit[$offset]s, " : 
	                $_   ? "$_ $unit[$offset], " : "";
	     $offset++;
	  } split ':', DateCalc($first,$last,\$err,1);
	  $length =~ s/,\s+$//g;
	  $length =~ s/^\s+//g;
	  #$length = DateCalc($last,$first	,\$err,1);

	  $timeSpan = "
	     <tr>
	         <td><b> Start: </b> </td>
	         <td><font size=-1>$start</font> </td>
      	     </tr><tr>
	         <td><b> End:   </b> </td>
		 <td><font size=-1>$end  </font> </td>
      	     </tr><tr>
	         <td><b> Length:   </b> </td>
		 <td><font size=-1>$length  </font> </td>
	     </tr>
	  ";
	  #################### RRD BUG
	   $timeSpan = "";
	  #################### RRD BUG
       }
    }       	     
	   
   return join("\n", 
           start_form(-name => tstatForm ),	     
	   "\n<TABLE width='100%'>",	   
 	       "<hidden NAME=menu 	VALUE='1'>\n",
	       "<hidden NAME=var 	VALUE='$pVar'>\n",
	       "<hidden NAME=dir 	VALUE='$pDir'>\n",
	       "<hidden NAME=template 	VALUE='$pTpl'>\n",
	       "<hidden NAME=duration 	VALUE='$pLen'>\n",
	       "<hidden NAME=logscale 	VALUE='$pLog'>\n",
	       "<hidden NAME=bigpic 	VALUE='$pBigpic'>\n",
	       "<hidden NAME=hifreq 	VALUE='$pHifreq'>\n",
#######	       "<hidden NAME=aggpic 	VALUE='$pAggpic'>\n",
	       "<hidden NAME=direction 	VALUE='$pDirection'>\n",
	       "<hidden NAME=exclude 	VALUE='$pExclude'>\n",
	       "<hidden NAME=include 	VALUE='$pInclude'>\n",
	   "\n<tr><td>",	       
               "<b> Trace: </b>",
           "</td><td>",   
		    popup_menu(-name=>'tstatMenuDir',
 		       	       -onChange => $jsMenuDir,
			       -default  => $pDir_default,
                               -values   => \@pDir,
			       -attributes => \%pDirAttr,
			       -labels   => \%pDir, ),		
		    button(-name=>'tstatMenuBtn',
                             -value=>'Start Over ',
                             -onClick=>$jsMenuBtn),			       
		    button(-name=>'tstatMenuBtn',
                             -value=>'Home',
                             -onClick=>$jsHomeBtn),						     
	   ( $pDir eq "$RRD_DATA" ) ? '' :			     
  		    button(-name=>'tstatMenuBtn',
                             -value=>'RRdata',
                             -onClick=>"location.href='/$pDir'"),			  
	   ## Access to RRD database
           ##"<a href='/$pDir'>[RRData]",
	   
			     
           "\n</td></tr> $timeSpan",   
 	       # "<br>",
 	#   ____________________________  
	#  /				\ 
	# /    splitvar       __________/ 
	# \__________________/.:nonsns:.  
	# 				  
	splitvar_print_menu(),


 	       # "<br>",
	       $pVar =~ m/NULL/ ? '' :
		     join(" ",
        		  # "<br>",     
	   	      "\n<tr><td>",	       
        		  "<b> Options: </b>",
	               "</td><td>",   
	 #  "<tr><td>",	       
	 #      "<b> Direction </b>",
         # "</td><td>",   
		    popup_menu(-name=>'tstatMenuVar',
 		       	       -onChange   => $jsDirection,
			       -default    => $pDirection,
                               -values     => \@pDirection,
			       -attributes => \%pDirectionAttr,
			       -labels     => \%pDirection, ),			  
        #   "</td></tr>";
		       
		       
   ########			     
# superceded by splitdirection			     
#                        checkbox_group(-name=>'tstatCheckAgg',
#                 	     -values =>['Aggregated'],
# 			     -default => [$pAggpic eq 'true' ? 'Aggregated' : ''],
# 			     -onClick => $jsCheckAgg) ,
#######
 		      checkbox_group(-name=>'tstatCheckDes',
 			  -values =>['Describe...'],
 			  -default => [$pDescribe eq 'true' ? 'Describe...' : ''],
 			  -onClick => $jsCheckDes) ,

                       checkbox_group(-name=>'tstatCheckAdv',
                	     -values =>['Advanced...'],
			     -default => [$pAdvopt eq 'true' ? 'Advanced...' : ''],
			     -onClick => $jsCheckAdv) ,
			     
		       checkbox_group(-name=>'tstatCheckCmd',
                	     -values =>['RRDcmd'],
			     -default => [$pAdvcmd eq 'true' ? 'RRDcmd' : ''],
	 		     -onClick => $jsCheckCmd) ,

           		"</td></tr>",   
        	     ),		   
		     
		        
            ($pVar !~ m/NULL/ ) && 
            $pAdvopt eq 'true' ?
	       join( " ", 
	   	      "\n<tr><td>",	       
        		  "<b> Advanced: </b>",
	               "</td><td>",  
 		       "Ymin: ",
		       textfield(-name=>'tstatYmin',
                                   -default=>$pAutoconf eq 'true'? 'auto' : $pYmin,
                                   -override=>1,
                                   -size=>5,
                                   -maxlength=>10, 
				   -onChange => $jsYmin),
		       "Ymax: ",
		       textfield(-name=>'tstatYmax',
                                   -default=>$pAutoconf eq 'true' ? 'auto' : $pYmax,
                                   -override=>1,
                                   -size=>5,
                                   -maxlength=>10,
				   -onChange => $jsYmax), 
				   
                       checkbox_group(-name=>'tstatAutoconf',
                	     -values =>['Autoconf'],
			     -default => [$pAutoconf eq 'true' ? 'Auto' : ''],
			     -onClick => $jsAutoconf) ,
                       checkbox_group(-name=>'tstatCheckLog',
                	     -values =>['Log'],
			     -default => [ $pLog eq 'true' ? 'Log' : ''],
			     -onClick => $jsCheckLog) ,
                       checkbox_group(-name=>'tstatCheckBig',
                	     -values =>['Bigpic'],
			     -default => [$pBigpic eq 'true' ? 'Bigpic' : ''],
			     -onClick => $jsCheckBig) ,
                       checkbox_group(-name=>'tstatCheckHif',
                	     -values =>['HiFreq'],
			     -default => [$pHifreq eq 'true' ? 'HiFreq' : ''],
			     -onClick => $jsCheckHif) ,

	   	      "</td></tr>",	       
# 	   	      "<tr>
# 		       <td> &nbsp </td>
# 		       <td>",	       
#NEWVAR 
#                        checkbox_group(-name=>'tstatCheckNEWVAR',
#                 	     -values =>['NEWVAR'],
# 			     -default => [$pNEWVAR eq 'true' ? 'NEWVAR' : ''],
# 			     -onClick => $jsCheckNEWVAR) ,
#NEWVAR 
	   	      "</td></tr>",	       
	       ) : "",		     
           end_form,
        );
}

#   ____________________________  
#  /				\ 
# /  split direction  __________/ 
# \__________________/.:nonsns:.  
# 				  
sub split_direction_failback {  
   undef @pDirection;


   if( $pVar eq 'NULL' ) {
   	$pDirection = 'NONE';
  	$pDxxxxxxxx{'NONE'}='--Select a direction--';
	unshift @pDirection, 'NONE';
        #extremeDebug("DONTWORRY $pVar is $pAdirectional{$pVar}");
	goto DONTWORRY;
   } 
   push @pDirection, "both"   if have_rrd(qw(_in _out));
   map { push @pDirection, $_ if  have_rrd("_$_") } qw(in out loc);
   push @pDirection, "bothcs" if have_rrd(qw(_c2s _s2c));
   map { push @pDirection, $_ if  have_rrd("_$_") } qw(c2s s2c);

   my $only_adirectional_rrd = have_rrd("") && !have_rrd(qw(_in _c2s _s2c _out _loc));
   if ($pAdirectional{$pVar} || $only_adirectional_rrd) {
   	$pDirection = 'NULL';
  	$pDxxxxxxxx{'NULL'}='--Aggregate only--';
	unshift @pDirection, 'NULL';
        #extremeDebug("BEHAPPY $pVar is $pAdirectional{$pVar}");
	goto BEHAPPY;
   }   
   #extremeDebug("OTHER $pVar is $pAdirectional{$pVar}");
   
   #what if the selected direction is not among the available ones?
   my %pDxxxxxxxx;
   map { $pDxxxxxxxx{$_} = 1 } @pDirection;

   ##   open LOG,  ">> log";
   ##   print LOG "$pVar\t$pDirection\n";
   if ( ($pDirection eq 'NULL') || ($pDirection eq 'NONE')) {
   # transition Aggregate only => Incoming/Client
        $pDirection = "bothcs" if $pDxxxxxxxx{bothcs};
        $pDirection = "both"   if $pDxxxxxxxx{both};

   } elsif ( !$pDxxxxxxxx{$pDirection} ) {
   # transition  Incoming/Client => Aggregate only 
        $pDirection = "NULL"   if $pDxxxxxxxx{NULL};   
        $pDirection = "bothcs" if $pDxxxxxxxx{bothcs};
        $pDirection = "both"   if $pDxxxxxxxx{both};
   }
   ##   print LOG "$pVar\t$pDirection\n\n";
   ##   close LOG;

   DONTWORRY:   
   	my $patience = q/has a limit, and/;
   BEHAPPY:
   	my $this_cgi = q/is putting it to a fair trial/;

#   my %class = ( style=>"{ font-family : sans-serif; font-size : 10px; }" );
   my %class = ( style=>"font-family : sans-serif;" );
   map { $pDirectionAttr{$_} = \%class; } @pDirection;
}
#-----------------------------------------------

#   ____________________________  
#  /				\ 
# /    splitvar/dir   __________/ 
# \__________________/.:nonsns:.  
# 				  
sub splitvar_print_menu {
my @splitvar = qw(eth ip tcp udp mm L7 p2ptv video profile);
my %splitmatch = (   
    	'eth'   =>  '^eth',
    	'ip'   =>   '^(ip_|flow_|L3_)',
	'tcp'  =>   '^tcp_',	       
	'udp'  =>   '^udp_',	       
    	'mm'   =>   '^(mm_|rtp_|rtcp_|skype_|msn_|chat_)', 
    	'L7'   =>   '^(L7_|L4_|tcp_bitrate|udp_bitrate|http_bitrate|bt_|p2p_bitrate|tls_bitrate|google_)', 
    	'p2ptv'   =>   '^p2ptv_',
        'video' => '^(L7_VIDEO|L7_WEB|L7_WWW|web_bitrate|video_rate|www_bitrate)', 
    	'profile' =>   '^profile_', 
    );
my %splitxcld = (   
    	'eth'   =>   '^(flow_|ip_|tcp_|udp_|mm_|rtp_|rtcp_|skype_|msn_|chat_|bt_|p2p_)',
    	'ip'   =>   '^xxx_',
	'tcp'  =>   '^tcp_bitrate',
	'udp'  =>   '^udp_bitrate',	       
    	'mm'   =>   '^xxx_', 
    	'L7'   =>   '^(L7_VIDEO|L7_WEB|L7_WWW)',
    	'p2ptv' =>   '^xxx_', 
    	'video' =>   '^xxx_', 
    	'profile' => '^xxx_', 
    );
my %splitdescr = (
    	  'eth'   =>  'Stats::Ethernet',
    	  'ip'   =>   'Stats::IP',
	  'tcp'  =>   'Stats::TCP',
	  'udp'  =>   'Stats::UDP',
    	  'mm'   =>   'Stats::MMedia',
    	  'L7'   =>   'Stats::Classifier',
    	  'p2ptv' =>  'Stats::P2P-TV',
          'video' =>  'Stats::Video',
    	  'profile' => 'Stats::Profile',
    );
 
   # all pull-down menus have same length
   # my $len;
   # map { $len = length($description{$_}) if length($description{$_}) > $len }  keys %description;
   # $len  = 10;

   my @ret;
   foreach my $splitvar (@splitvar) {
       #@this_pVar = grep ( m/$splitmatch{$splitvar}/ && !m/$splitxcld{$splitvar}/ , @pVar);
       @this_pVar = grep ( m/$splitmatch{$splitvar}/ , @pVar);
       @this_pVar = grep ( !m/$splitxcld{$splitvar}/ , @this_pVar);
#       die "@this_pVar";
        
       # all pull-down menus have same length
       # map { $this_pVar{$_} = sprintf "%${len}s", $description{$_} } @this_pVar;
       map { $this_pVar{$_} = $description{$_} } @this_pVar;
#       %class = ( style=>"{ font-family : sans-serif; font-size : 10px; }" );
       %class = ( style=>"font-family : sans-serif;" );
       map { $this_pVarAttr{$_} = \%class; } @this_pVar;

       my $space = '----'x7;
       $this_pVar{'NULL'}="$space Select a parameter $space";
       unshift @this_pVar, 'NULL';
       $this_pVar = ( $pVar !~ m/^$splitvar/ ) ? 'NULL' : $pVar;
       #        if( $pVar !~ m/^$splitvar/ ) {
       #        } else {
       #             my $space = '----'x7;
       #   	    $this_pVar{'NULL'}="$space--------------------$space";
       # 	    unshift @this_pVar, 'NULL';
       #             $this_pVar = $pVar;
       #        }
       
       if ( @this_pVar ) {
       push @ret, join " ",
	   "<tr><td>",	       
	       "<b> $splitdescr{$splitvar} </b>",
           "</td><td>",   
		    popup_menu(-name=>'tstatMenuVar',
 		       	       -onChange => $jsMenuVar,
			       -default  => $this_pVar,
                               -values   => \@this_pVar,
			       -attributes => \%this_pVarAttr,
			       -labels   => \%this_pVar, ),			  
           "</td></tr>";
       }	   
    }  
    return join "\n", @ret; 
}	   
	   


#   ____________________________  
#  /				\ 
# /    menuHtml       __________/ 
# \__________________/.:nonsns:.  
# 				  
#  if you want to add a templa e or a time-scale,
#  you need to modify this
#
sub menuHtml {
my $html;
my @pTpl = qw(avg stdev hit idx prc normidx);
my %pTpl = ();  
my @pLen;

#tstat v.1.2.0, tstat_rrd.gci 2.5: high frequency RRD for short traces
#map { push @pLen, "$RRD_TIME{$_}$_" } qw(h d wk m y); 
    @pLen =  @RRD_TIME;
    
    $format_loose = 0;
    $space = $format_loose ? " " : "";


split_direction_failback(); # if( $pDirection eq '');

my $PSPLITVAR = ( $pDirection eq 'bothcs' && $pServerifiable{$pVar} )  ? '_c2s' :
		( $pDirection eq 'both' ) ? '_in'  : 
		( $pAdirectional{$pVar} ) ? ''     :
		( $pDirection eq 'NONE' ) ? ''     :
		( $pDirection eq 'NULL' ) ? ''     :
		( $pDirection ne '' )     ? "_$pDirection" : 
					    '';

    
#===============================================
# check for availablte templates
#-----------------------------------------------
  $pTpl{avg}=1 
    if( -e "$pDir/$pVar${PSPLITVAR}.avg.rrd" && 
        -e "$pDir/$pVar${PSPLITVAR}.min.rrd" && 
        -e "$pDir/$pVar${PSPLITVAR}.max.rrd");
#    if( -e "$pDir/$pVar${PSPLITVAR}${RRD_TREE}avg.rrd" && 
#        -e "$pDir/$pVar${PSPLITVAR}${RRD_TREE}min.rrd" && 
#        -e "$pDir/$pVar${PSPLITVAR}${RRD_TREE}max.rrd");

  $pTpl{stdev}=1 
   if( -e "$pDir/$pVar${PSPLITVAR}.avg.rrd" && 
       -e "$pDir/$pVar${PSPLITVAR}.stdev.rrd");
	  
  $pTpl{hit}=1 
   if( -e "$pDir/$pVar${PSPLITVAR}.hit.rrd");
	 
  map {	 
        my @file = glob("$pDir/$pVar${PSPLITVAR}.$_*.rrd");
	  $pTpl{$_}=1 if $#file >= 0; 	  
  } qw(prc idx);	  
  

  my $templateCount = 0;
  map { $templateCount++ if $pTpl{$_} }	keys %pTpl;
  $pTpl{normidx} = $pTpl{idx};
  

#  extremeDebug( $PSPLITVAR, "ADIR=$pAdirectional{$pVar}, PSRV=$pServerifiable{$pVar}", $pDirection, "PATH=$pVar/$pDir", glob("$pDir/$pVar*rrd"),  \@pTpl, \%pTpl)
#   	unless $templateCount;

#===============================================
# menu: pasting formHtml, Template, Time together
#-----------------------------------------------
  if ($pVar eq 'NULL' ) {
      # when you first enter a directory, you MUST set pVar = NULL 
      # this make cgi display the pDir/README[.html] file  
      $form = formHtml();
      return returnHtml( formHtml(), "</table>", $pReadme ); 
      
  } else {
      $html .= "<!-- MENU_START -->\n\n";

      # if not all the files to render $pTpl are there, fall back on first avail	
      $pTpl = '' unless $pTpl{$pTpl};

      #IT's a TABLE now!!!
      $html .= formHtml();
      my $templateFirst = "";
      #
      # display first template available by default
      #
      $html .= "<tr><td>";
      $html .= "<b> Template: </b>";
      $html .= "</td><td>";
      unless ( $templateCount ) {
	 $html .= "<i>No template available for the selected trace and metric </i>"       
      } else {
	 foreach my $t ( qw(stdev avg hit prc idx normidx) ) {
	       next unless $pTpl{$t};
	       $templateFirst = $t if $templateFirst eq ""; 
	       my $tlab = describeTemplate($t);

               #### $href = "href=$tstat_rrd_cgi?dir=$pDir&var=$pVar&template=$t&hifreq=$pHifreq&duration=&bigpic=$pBigpic&loscale=$pLogscale&aggpic=$pAggpic";
	       $href = "href=$tstat_rrd_cgi?dir=$pDir&var=$pVar&template=$t&exclude=$pExclude&include=$pInclude&hifreq=$pHifreq&duration=&bigpic=$pBigpic&logscale=$pLog&direction=$pDirection";	    
	       if ($pLen ne "") {
		  # specific time chosen: pletora of templates
		  $html .=  "[$space<a $href>$tlab</a>$space]" ;

	       } else {
 		  $html .= (($pTpl eq "") && ($t eq $templateFirst)) || 
	       		   (($pTpl ne "") && ($t eq $pTpl)) # || ($templateCount == 1) 
			   ? "\<<b>$tlab</b>\>" :
			     "[$space<a $href>$tlab</a>$space]";
               }  
	       $html .=  "&nbsp"x($format_loose ? 4:2);
	       $html .=  "\n";
	 } 
	 $html .= "</td></tr>";
	 $pTpl  = $templateFirst  if (($pLen  eq '') and ($pTpl eq ''));
      }
      #
      # display h,d,w,m,y timescale by default
      #
      $html .= "<tr><td>";
      $html .= "<b> Time:  </b>&nbsp&nbsp";
      $html .= "</td><td>";
      foreach my $d (@pLen) {
	    my $dlab = describeDuration( $d );
            $dlab =~ s/\s*Graph\s*//g; 
	    
            ### $href = "href=$tstat_rrd_cgi?dir=$pDir&var=$pVar&template=&hifreq=$pHifreq&duration=$d&bigpic=$pBigpic&loscale=$pLogscale&aggpic=$pAggpic";
            $href = "href=$tstat_rrd_cgi?dir=$pDir&var=$pVar&exclude=$pExclude&include=$pInclude&template=&hifreq=$pHifreq&duration=$d&bigpic=$pBigpic&logscale=$pLog&direction=$pDirection";
            $html .= ( $d eq $pLen ) ? "\<<b>$dlab</b>\>" : "[$space<a $href>$dlab</a>$space]";
	    $html .=  "&nbsp"x($format_loose ? 4:2);
	    $html .=  "\n";
      }      
      $html .= "</td></tr>";

      #$html .= "\n<br><b> Time Scale: </b>&nbsp&nbsp";
      #      $html .= "[<a href=tstat_rrd.cgi?param=$param&timescale=0.5><b>/2</b></a>]";
      #      $html .=  "&nbsp"x4;
      #      $html .= "[<a href=tstat_rrd.cgi?param=$param&timeshift=-1><b>-1</b></a>]";
      #      $html .=  "&nbsp"x4;
      #      $html .= "[<a href=tstat_rrd.cgi?param=$param&timereset=1><b>Reset</b></a>]";
      #      $html .=  "&nbsp"x4;
      #      $html .= "[<a href=tstat_rrd.cgi?param=$param&timeshift=+1><b>+1</b></a>]";
      #      $html .=  "&nbsp"x4;
      #      $html .= "[<a href=tstat_rrd.cgi?param=$param&timescale=2><b>*2</b></a>]";
      #      $html .=  "\n";
	
      $html .= "</TABLE>";	
      return returnHtml( $html, 
      "<p><hr> It seems that no template is available for the 
      selected combination of trace (<B>$pDir</B>) <br>
      and metric (<B>$description{$pVar}</B>): try changing some 
      of the above settings <br>($pDirection:$PSPLITVAR)" ) 
      	  if !$templateCount && ($pVar ne '');
      
      # when no args are passed to the script
      return returnHtml( $html ) unless $templateCount;
      #XXX       } else {
      #        	    verb("Templates available ($param,$template,$duration)");
      #   	    map { verb("\t$_") } keys %tmpl;
      #XXX       }   
  }    	
  $html .= "<!-- MENU_END -->\n\n";  
  $htmlmenu = $html;


#===============================================
# describe
#-----------------------------------------------
    $htmlmenu .= describePlot() if $pDescribe eq 'true';
  
#===============================================
# plots: pasting images and form
#-----------------------------------------------
  if (($pLen eq '') or($pTpl eq '') ) {
      verb("MENU: given template ($pTpl), loop over time") if ($pLen eq '') ;
      verb("MENU: given duration ($pLen), loop over template") if ($pTpl eq '');
  
      my @X = ($pLen eq '') ? @pLen : @pTpl;
 
      $html = "\n";
      X:
      foreach my $x (@X) {
            my ($imagef,$dlab,$epsf);	    
	    if ($pLen eq '') {
            # given template, loop over time
		     ($imagef,$cmdf) = applyTemplate( graphTemplate($pDir,$pVar,$pTpl,$x) );   	    
		     $dlab = describeDuration( $x );
	    } else {    
            # given duration, loop over template
	    	next X unless $pTpl{$x};
        	      ($imagef,$cmdf) = applyTemplate( graphTemplate($pDir,$pVar,$x,$pLen)  );   
		      $dlab = describeTemplate( $x );		      
	    }	    
	    $epsf = $imagef; 
	    $epsf =~ s/png/eps/g;

	    #   ____________________________  
	    #  /			    \ 
	    # /    eps            __________/ 
	    # \__________________/.:nonsns:.  
	    # 				  
	    # are hidden to the rest of the world...
	    $jsAddToGallery="javascript:
	    	newwindow=window.open(\"$tstat_rrd_cgi?gallery_add=$imagef&gallery_cmd=$cmdf&var=$pVar&dir=$pDir&direction=$pDirection\");
		if(windod.focus){ 
			newwindow.focus() 
		}";


	    my $other_formats = hidden_stuff() ? "" :
	        "&nbsp&nbsp
		<font size=-3> 
		<a href='/$epsf'>[PostScript]</a> &nbsp&nbsp
		<a href='$jsAddToGallery'>[Add to Gallery]</a> &nbsp&nbsp
                </font>"; 

	    $html .= join("", "<h2> $dlab $other_formats </h2>\n",
	                       ( -e $imagef ) ? 
			       		"<img src='/$imagef'></img>" : 
					"<pre> $imagef </pre>",
     			 "\n<br><br><hr>\n");
      }			 
  } else {
     die join("\n", "Oops, I cannot quite make it out...
       dir=$pDir
       var=$pVar
       log=$pLog
       len=$pLen
       tpl=$pTpl
       ");
  }

  return returnHtml(  $htmlmenu, $html  );
}


#   ____________________________  
#  /				\ 
# /    describePlot   __________/ 
# \__________________/.:nonsns:.  
# 	
sub describePlot {
   my $anchor = $pVar;
      $anchor  =~ s/_(in|out|c2s|s2c|loc)$//g;

   
   my $tdes;
   if ($pLen ne '') {
      $tdes = "You are now seeing, for a specific <B>timespan</b> (
       @{[describeDuration($pLen)]} ), 
      all the available templates for the selected metric
      (<a target=help href='http://tstat.tlc.polito.it/measure.html#$anchor'> $description{$pVar}</A>). 
      To get the description of a specific <b>template</b> you have to select it first,
      and observe it at different time granularities.",
   } else {
      $tdes = "You are now seeing, a specific <B>template</b> (
      @{[describeTemplate($pTpl)]} </a>), 
      over all the available timespans for the selected metric (
      <a  target=help href='http://tstat.tlc.polito.it/measure.html#$anchor'> $description{$pVar}</a>). 
      $templateDescription{$pTpl}"
   }
   return "
   <hr>
   <h2> Description </h2>
   <table border=0 width=625>
   <!-- -->
   <tr><td colspan=2><B> Metric Description: </B> </td></tr>
   <tr><td>  &nbsp &nbsp &nbsp </td><td>
   	<iframe SCROLLING=no
	 frameborder=0
	 width=800
	 height=100 src='http://tstat.tlc.polito.it/measure.html#$anchor'>
	</iframe>
   </td></tr>
   <!-- -->
   <tr><td colspan=2> <B> Template Description: </B><br> </td></tr>   	
   <tr><td> &nbsp &nbsp &nbsp </td><td>
     <p align=justify>
	$tdes
	</p>
   </td></tr>
   </table>
   <hr>
   ";
   
}


#   ____________________________  
#  /				\ 
# /    applyTemplate  __________/ 
# \__________________/.:nonsns:.  
# 	
sub applyTemplate {
   # support library or system call   
    verb("RRDs::graph($param,$template,$duration)");
    $filename = $_[0];
    $cmdfile="$filename.RRDtool";

    if ( $pAdvcmd eq 'true' ) {
         return join( "", 
	 "/usr/local/rrdtool/bin/rrdtool graph \\\n\t'", (join "' \\\n\t'", @_), "'");
    }

    # png
    #     shift @_;
    #     unshift @_, ($filename, '--vertical-label','Tstat/RRD');
    open CMD, "> $cmdfile";
    print CMD "rrdtool graph\n\t", join("\n\t", map { "'$_'" } @_) ;
    close CMD;
    RRDs::graph(@_);
    my $ERR=RRDs::error;
    die join  ("\n", "ERROR while drawing: $ERR \nfrom\nrrdtool graph\n\t", join("\n\t",@_))
 		if $ERR;

    #eps 
    shift @_;
    unshift @_, ($filename, '--font','DEFAULT:14:TimesBold');
    map { 
    	m/PNG/ and s/PNG/EPS/; 
   	m/png/ and s/png/eps/; 
    } @_;
    RRDs::graph(@_);
    $ERR=RRDs::error;
    die join  ("\n", "ERROR while drawing: $ERR \nfrom\nrrdtool graph\n\t", join("\n\t",@_))
 		if $ERR;

   return wantarray ? ($filename,$cmdfile) : $filename; #image filename
}

#   ____________________________  
#  /				\ 
# /   graphTemplate   __________/ 
# \__________________/.:nonsns:.  
# 				  
#
#  the intelligence of tstat_rrd.cgi
#  this turns files into nice and colored graphs
#
sub graphTemplate {
my ($dir,$var,$template,$duration)=@_;
my (@RRDpar,@RRDoth);
   $param = "$dir/$var";

   $imagef = "$param$RRD_TREE$template.$duration.png"; 
   $imagef =~ s{^/+}{}g; # chomp initial /
   $imagef =~ s{/+}{/}g; # chomp multiple //
   $imagef =~ s{/}{.}g;  # turn / into . 
   $imagef = "$IMG_DIR/$imagef";
   #--imginfo '<IMG SRC="/img/%s" WIDTH="%lu" HEIGHT="%lu" ALT="Demo">'

   my $par;
   if($RRD_TREE=='.') {
      $par = (split '\.', (split '\/', $param)[-1])[0]
   } else {
      $par = (split '\/', $param)[-2]
   }

   # aggregate 
   my ($other,$oth,@oth);
   my ($partag,$othtag)=("","");
   
   
#===============================================
#  splitDirection
#-----------------------------------------------
   $other = "NULL";
   if ( $pAdirectional{$par} ) { 
	# nothing special to do
	
   } elsif ( $pServerifiable{$par} && $pDirection =~ m/(c2s|s2c)/ ) {
  	$param .= "_$pDirection";  
   	$par   .= "_$pDirection"; 

   } elsif ( $pDirection =~ m/(in|out|loc)/ ) {
  	$param .= "_$pDirection";  
   	$par   .= "_$pDirection"; 
   
   } elsif ( $pServerifiable{$par} && $pDirection eq 'bothcs' ) {  
  	 $other = $param;
	 $oth = $par;
         $param  .= "_c2s";  
	 $par    .= "_c2s";
	 $partag .= " (c2s)";
         $other  .= "_s2c";  
	 $oth    .= "_s2c";
	 $othtag .= " (s2c)";

   } elsif ( $pDirection eq 'both' ) {  
  	 $other = $param;
	 $oth = $par;
         $param  .= "_out";
	 $par    .= "_out";
         $partag .= " (out)";  
         $other  .= "_in";  
	 $oth    .= "_in";
	 $othtag .= " (in)";
   } else {
      die join "\n", "No idea how we got there!", $param, $par, $other, $pDirection;
   } 


   #my $title = "$description{$par} [@{[describeTemplate($template)]}]";
   
   my $title = "$description{$par}";
   if ($other ne "NULL")  {
   	$title .= "  [out (+) in (-)]" if ($pDirection eq 'both');
   	$title .= "  [client (+) server (-)]"     if ($pDirection eq 'bothcs');
   }

   push @RRDpar, $imagef, 
                 '--imgformat', 'PNG';
		 # '--color', "'BACK=$color{gray}'";
   push @RRDpar, '--logarithmic' 
   		if $pLog eq 'true'; 		
   # any satanic reference is purely coincidental:
   # 666 is closest integer such that multiplied by
   # the selected zoom factor picture width is 800
   push @RRDpar, '--width', '666',  '--height', '200' 
   		if $pBigpic eq 'true';
   push @RRDpar, '--zoom', '1.18';
     
   # upper limit
   my $rigid=0;
   if ( $template =~ m/normidx/ && 
      (( $pAutoconf eq 'true') || ($pYmax eq ""))) {
      $rigid=1;
      push @RRDpar, "--rigid", "--upper-limit", 100;
   } elsif( ($pYmax ne "") && ( $pAutoconf ne 'true' )) {
      $rigid=1;
      push @RRDpar, "--rigid", "--upper-limit", "$pYmax";
   }		   
 
   if( ($pYmin ne "") && ( $pAutoconf ne 'true' )) {
   	push @RRDpar, "--rigid" unless $rigid;
   	push @RRDpar, "--lower-limit", "$pYmin";
   }
		

   my $template_suffix = ( $template eq 'normidx' ) ? 'idx' : $template;
   if( $duration ne "" && 
      -e ($file = (glob "$param${RRD_TREE}${template_suffix}*.rrd")[0] )) {         
      #AWFUL trick to account for (idx|prc)*
       $last = RRDs::last("$file");
       $last_date = ctime($last);
       push @RRDpar, 
       		 '--title', "$title - Last: $last_date",
                 "--end", "$last",
       		 "--start", "end-$duration";
		     
   } else {
   	warn "Duration $duration was specified, but no file $file 
	found by globbing $param${RRD_TREE}${template}*.rrd 
        ... ignoring"
   }	      
   
   # At this point, 
   #
   # $param = rrd_data/Polito/2000/May/protocol_out 
   # $par = protocol_out
   #
   my ($x,$X)=(0,'A');
   my @par;
    
   
   if ($template =~ m/(stdev)/ ) { 
       #
       # this one is special
       #
       push @RRDpar, 	
       	"DEF:avg=$param${RRD_TREE}avg.rrd:$par:AVERAGE",
        "DEF:stdev=$param${RRD_TREE}stdev.rrd:$par:AVERAGE",
#        "CDEF:p3s=avg,stdev,3,*,+",
        "CDEF:p1s=avg,stdev,+",
#      	"LINE1:p3s$color{dred}: Average + 3*Stdev",
	"LINE2:p1s$color{red}: Average + Stdev",
        "LINE3:avg$color{orange}: Average";

	if ($other ne 'NULL') {
	  push @RRDpar, 	
       	   "DEF:oth_avg=$other${RRD_TREE}avg.rrd:$oth:AVERAGE",
           "DEF:oth_stdev=$other${RRD_TREE}stdev.rrd:$oth:AVERAGE",
           "CDEF:neg_avg=0,oth_avg,-",
#           "CDEF:neg_p3s=neg_avg,oth_stdev,3,*,-",
           "CDEF:neg_p1s=neg_avg,oth_stdev,-",
#       	   "LINE1:neg_p3s$color{dred}:",
       	   "LINE2:neg_p1s$color{red}:",
       	   "LINE3:neg_avg$color{orange}:";	
	}
	
#die join "\n", @RRDpar;
        return @RRDpar;			

   } elsif ($template =~ m/(hit)/ ) {
       @par = qw(hit);

   } elsif ($template =~ m/(avg|max|min)/ ) {
       @par = qw(min avg max);
	
   } elsif ($template =~ m/(normidx|idx|prc)/ ) {
   	my $template_suffix = ( $template eq 'normidx' ) ? 'idx' : $template;
	map { 
#		push @par, "$1$2" if m/(idx|prc)(\d+\.*\d*|oth)\.rrd/;
                if (m/(idx|prc)(\d+\.*\d*|oth)\.rrd/)
		  { 
                    ($excl=$2) =~ s/(idx|prc)//;
                    $excl = -1 if ($excl eq "oth");
                     
                    if (exists($pExclude{'ALL'}))
                     {
                       push @par, "$1$2" if (exists($pInclude{$excl}));
                     }
                    else
                     {
                       if (!exists($pExclude{$excl}))
                        {
                          push @par, "$1$2";
                        }
                       elsif (exists($pInclude{$excl}))
                        {
                          push @par, "$1$2";
                        } 
                     } 
                  } 
	} glob "$param${RRD_TREE}$template_suffix*rrd";
	@par or die "No indexes for $template_suffix for $param";
	@par = sort { 
	   ($numA=$a) =~ s/(idx|prc)//;
	   ($numB=$b) =~ s/(idx|prc)//;
	   #oth is always last"
           $numA = $idx2value->{$par}{$numA}[2] if exists($idx2value->{$par}{$numA}[2]);
           $numB = $idx2value->{$par}{$numB}[2] if exists($idx2value->{$par}{$numB}[2]);
	   return ( $a eq "oth" ) ? 1 :
	          ( $b eq "oth" ) ? -1 :
	          m/idx/ ? $numA <=> $numB :
		           $numB <=> $numA;  # care to this order
        } @par;
   } else {
   	die "Man, $template is no template I know";
   }

	
   $kind = lineStyle($template,0);

   my @RRD_posdef;
   my @RRD_negdef;
   my @RRD_poscdef;
   my @RRD_poscdef2;
   my @RRD_negcdef;
   my @RRD_negcdef2;
   my @RRD_posline;
   my @RRD_negline;
   
   #for normidx
   my $sumpos="CDEF:pos_sum=0";
   my $sumneg="CDEF:neg_sum=0";
   map {

      if( -e ($file = "$param$RRD_TREE$_.rrd" )) {
         $kind = lineStyle($template,$x);
	 ####XXX $line = "$kind:$X$defColor[$x]:$description{$par} (@{[labelOf($_)]})";

	 #partag is empty if Aggpic=false
#	 $line = "$kind:pos_$X$defColor[$x]:@{[labelOf($par,$_)]}";
	 $line = "$kind:pos_$X@{[colorOf($par,$_,$x)]}:@{[labelOf($par,$_)]}";
         $def = "DEF:$X=$file:$par:AVERAGE";
         $cdef2 = "CDEF:c_$X=$X,UN,0,$X,IF";
         $cdef = "CDEF:pos_$X=c_$X";
         $cdef .= ",100.0,*,pos_sum,/" if $template =~ m/normidx/;
	 $sumpos .= ",c_$X,+";
	 	 
	 push @RRD_posdef, $def;
	 push @RRD_poscdef, $cdef;
	 push @RRD_poscdef2, $cdef2;
	 push @RRD_posline, $line;	            

  	 if ($other ne 'NULL') {
	    if(-e ($othfile="$other$RRD_TREE$_.rrd") ) {
	       
	       #$kind='STACK' if ( $kind eq 'AREA' and $par =~ m/idx/ );
	       
	       $line = "$kind:neg_$X@{[colorOf($par,$_,$x)]}:";#@{[labelOf($par,$_)]}$othtag";
               $def = "DEF:oth_$X=$othfile:$oth:AVERAGE";
  	
               $cdef2 = "CDEF:c_oth_$X=oth_$X,UN,0,oth_$X,IF";
	       $cdef = "CDEF:neg_$X=0,c_oth_$X,-";
	       $cdef .= ",100.0,*,neg_sum,/" if $template =~ m/normidx/;
	       
               $sumneg .= ",c_oth_$X,+";
	       push @RRD_negdef, $def;
	       push @RRD_negcdef, $cdef;
	       push @RRD_negcdef2, $cdef2;
	       push @RRD_negline, $line;	            
	    } else {
	       die "Woops! $othfile ($other) does not exist!"
	    }    	    
	 }
	 
	 $X++ and $x++;	 
      } else {
	 die "ing: file $file was not found to build template $template";
      }   
   } @par;
   
   push @RRDpar, (@RRD_posdef, @RRD_poscdef2, $sumpos, @RRD_poscdef, @RRD_posline);
   push @RRDpar, (@RRD_negdef, @RRD_negcdef2, $sumneg, @RRD_negcdef, @RRD_negline)
	   if ($other ne 'NULL');


  return @RRDpar;

  # do not wanna die...
  #
  #   # GRAPH
  #   die "/usr/local/rrdtool/bin/rrdtool graph \\\n'", (join "' \\\n\t'", @RRDpar);
  # 
  #   # EXPORT
  #   die "/usr/local/rrdtool/bin/rrdtool xport \\\n'", (join "' \\\n\t'", 
  #   @RRD_posdef, $sumpos, @RRD_poscdef,  'XPORT:pos_sum	', 'XPORT:pos_A'), "'\n";
}

#   ____________________________  
#  /				\ 
# /    label & Co.    __________/ 
# \__________________/.:nonsns:.  
# 				  
#
#  description of labels, lineSyles, durations, etc.
# 
sub labelOf {
my ($par,$idx) = @_; 
  local $_ = lc("$idx");
       if( m/min/ )     {  return 'Minimum'
  } elsif( m/max/ )     {  return 'Maximum'
  } elsif( m/avg/ )     {  return 'Average'
  } elsif( m/var/ )     {  return 'Variance' 
  } elsif( m/stdev/ )   {  return 'Standard Deviation'
  } elsif( m/idx(.*)/ ) {  return $1 ne "oth" ? describeIdx($par,$1) : "Others"
  } elsif( m/prc(.*)/ ) {  return $1 ne "oth" ? "$1-th Percentile" : "Others"
  } elsif( m/hit/ )     {  return "Hit Counter"
  } else {
	  return "Unknown parameter statistics $1 ... "
  }	  
}

sub describeIdx {
my ($par,$idx) = @_; 
   #print Dumper($par,$idx,$idx2value);
   if( exists $idx2value->{$par}{$idx} && $idx2value->{$par}{$idx}[0] ne "" ) {
        $longest = 0;
	map { 
		$len = length($idx2value->{$par}{$_}[0]);
 	        $longest = $len if  $longest < $len;
        } keys %{ $idx2value->{$par} };
	#$longest += 3;
	return sprintf "%-${longest}s", $idx2value->{$par}{$idx}[0];
   	# return join(" ", $idx2value->{$par}{$idx}, " "x20)
   }
   return "$par = $idx";
} 

sub colorOf {
my ($par,$idx,$x) = @_; 
  local $_ = lc("$idx");
       if( m/min/ )     {  return $defColor[$x]
  } elsif( m/max/ )     {  return $defColor[$x]
  } elsif( m/avg/ )     {  return $defColor[$x]
  } elsif( m/var/ )     {  return $defColor[$x] 
  } elsif( m/stdev/ )   {  return $defColor[$x]
  } elsif( m/idx(.*)/ ) {  return $1 ne "oth" ? colorIdx($par,$1,$x) : $color{'msblue'}
  } elsif( m/prc(.*)/ ) {  return $defColor[$x]
  } elsif( m/hit/ )     {  return $defColor[$x]
  } else {
	  return $defColor[$x];
  }	  
}

sub colorIdx {
my ($par,$idx,$x) = @_; 
   #print Dumper($par,$idx,$x);
   if( exists $idx2value->{$par}{$idx} && $idx2value->{$par}{$idx}[1] ne "" ) {
	return $color{$idx2value->{$par}{$idx}[1]} || $defColor[$x];
   	# return join(" ", $idx2value->{$par}{$idx}, " "x20)
   }
   return $defColor[$x];
}


sub lineStyle {
  local $_ = lc(shift);
  $num = shift;
  if( m/(min|max|avg|var|stdev|hit)/ )     {  
  	return 'LINE2'
  } elsif( m/idx/ )     {  
  	return $num ? 'STACK' : 'AREA'
  } elsif( m/prc/ )     {  
  	return 'LINE2'; ##'AREA'; #they must be carefully sorted
  } else {
	return "Unknown parameter statistics $1 ... "
  }	  
}

sub describeTemplate {
local $_ = shift;
    return "Hit Counter"	if m/hit/;
    return "Mean and Bounds"    if m/(avg|max|min)/; 
    return "Mean and Stdev"     if m/stdev/; 
    return "Normalized Values"  if m/normidx/;  
    return "Specific Values"    if m/idx/;  
    return "Distribution"       if m/prc/; 
    return "Unknown Template"   
}   	


%templateDescription = (
 	hit => "
Though I have coded this template, I have never seen one of these,
so I do not have any idea of what it should look like.",
 	avg => "
This template shows, as three distinct lines, the <B>minimum</b>, <B>average</b> and
<B>maximum</b> values achieved by the observed metric in the
given timespan, practically bounding the extent of its distribution.",
 	stdev => "
This template shows three distinct lines: the lowest is the <B>average</b> 
value achieved by the observed metric in the given timespan; the intermediate
is given by the sum of  <B>average + standard deviation</b>  and the 
upper is given by the sum of the former plus three times the latter.
This plot should not be interpreted in a B<quantitative> way, but in a rather
the <B>qualitative</b> way: indeed, these curves reflect the rate of change,
in the sense that a sharp peak correspond to an abrupt change of the observed 
metric, change which is further amplified by the intermediate and upper curves.",
	idx => "
This template shows several stacked areas, corresponding to the <b>raw amount</b>
of the observed metric the given timespan: each of the curves is a simple counter
of the number of times that  the observed metric achieved a specific value.
For example, these areas can count the number of packets of a given size as
well as the number of flows on a given port, or the TCP options negotiated;
finally, note that there is a corresponding normalized template.",
	normidx => "
This template shows several stacked areas, corresponding to the <b>normalized amount</b>
of the observed metric the given timespan: each of the curves are simple counters 
of the number of times that  the observed metric achieved a specific value,
normalized over the number of samples observed over the same timespan.
For example, these areas can count the percentage of packets of a given size as
well as the percentage of flows on a given port; finally, note that there is a 
corresponding  template which no not make use of normalization.",
	prc => "
This template shows several stacked areas, corresponding to the <b>quantiles</b>
of the distribution of the observed metric the given timespan; the time-varying 
distributions usually show the <B>statistical median</b> (which corresponds
to the 50-th percentile of the distribution) as well as the 90-th, 95-th and 99-th 
quantiles.",
);
 
	
$templateDescription{min}=$templateDescription{max}=$templateDescription{avg};



sub describeDuration {
local $_ = shift;

   if ( $pHifreq eq 'true' ) {
    return "1hr"  	        if m/^1h/;
    return "4hrs" 		if m/^4h/;
    return "12hrs"		if m/^12h/;
    return "24hrs"		if m/^24h/;
    return "48hrs"		if m/^48h/;
  } else {    
    return "Hourly Graph"  	if m/$RRD_TIME{h}h/;
    return "Daily Graph"  	if m/$RRD_TIME{d}d/;
    return "Weekly Graph"  	if m/$RRD_TIME{w}w/;
    return "Monthly Graph" 	if m/$RRD_TIME{m}m/;
    return "Yearly Graph"  	if m/$RRD_TIME{y}y/;
  }    
  return "Custom Duration ($_)"	      
}

#   ____________________________  
#  /				\ 
# /  Gallery Stuff    __________/ 
# \__________________/.:nonsns:.  
# 				  
use File::Copy;

sub gallery_newid {
my $id = "A000";
   while (-e "$RRD_GALLERY/$id.png") {
   $id++
   }
   return $id;
}


sub gallery_system {
my $cmd = "@_";
my  ($err,$msg)=system($cmd);
   return  $err ? "Troubles executing ``$cmd'':\n<br><br>System says: $msg, $err,$!, $@\n<br><br>" :
                   "Executed ``$cmd'' \n<br><br>";
}		   

sub gallery_copy {
local $" = " to ";
	$ok = 0;
 	return copy(@_) ? 
 		"Copied @_\n<br><br>" : 
 		"Troubles copying @_:\n<br><br>System says: $!\n<br><br>";
}

sub gallery_add {
my ($imf,$cmdf)=@_;
my $dir   = url_param("dir");
   $dir   =~ s/$RRD_DATA\///;
my $direc = url_param("direction");
   $direc = $pDirection{$direc};
my $stat  = url_param("var");   
   $stat = $description{$stat};
   
     print      
     returnHtml(
        "<h2> Tstat's Gallery </h2><hr>",
	"<img src='/$imf' />",
	"<p><i> Edit your HTML description of the above picture <br>",
        start_form(-name => 'galleryForm' ),	     
        textarea(-name=>'gallery_text',
                 -default=>"<b>Trace</b>: $dir<br>\n<b>Flows</b>: $direc<br>\n<b>Stats</b>: $stat<br>\n",
                 -rows=>10,
                 -columns=>50),
#         hidden(-name=>'gallery_add', $imf),		 
#         hidden(-name=>'gallery_cmd', $cmdf),		 
     "<br>",
	button(-name=>'Add to gallery...',
                 -onClick=>"javascript:location.href=\"$tstat_rrd_cgi?gallery_save=1&gallery_add=$imf&gallery_cmd=$cmdf&gallery_text=\" + document.forms.galleryForm['gallery_text'].value"),
	button(-name=>'...forget about it!',
                 -onClick=>'window.close()')
     );
     exit(0);
}       


sub gallery_show {
my $text = "";
my $gal_num = 0;
my $gallery_asnow = url_param("gallery_asnow");
   
    open LIST, "ls -1t $RRD_GALLERY/*.txt |";
    while(<LIST>) {
       chomp;
       s/.txt$//;
       $file = $_;
       next unless -e "$file.txt" && -e "$file.png" && -e "$file.cmd";
       $cat = join "",`cat "$file.txt"`;

       ;
       #note that file has RRD_GALLERY embedded. 
       #we add a / so that it starts from the HTML root
       # 	    $text .= "<tr>";
       # 	    $text .= ($gal_num++ % 2) ? 
       #               "<th><img src='/$file.png'></th>
       # 	       <td><hr><pre> $cat </pre><br><hr></td>" :
       # 	      "<td><hr><pre> $cat </pre><br><hr></td>
       #                <th><img src='/$file.png'></th>";	  
       # 	    $text .= "</tr>\n";
       open CMD, "$file.cmd";
       #my @cmd = map { chomp; $_ } `grep -v "rrdtool graph" "$file.cmd"`;
       my @cmd;
       while(<CMD>) {
	  chomp;
	  next if m/rrdtool/;

	  if (m/--end/) {
	     push @cmd, '--end=now';
	     <CMD>;
	  } else {
	     s/^\s*'//g;
	     s/\s*'\s*$//g;
	     push @cmd, $_
	  }   
       }
       
       close CMD;
       #@die "@cmd";
       
       RRDs::graph(@cmd);
       my $ERR=RRDs::error;
       die join  ("\n", "ERROR while drawing: $ERR \nfrom\nrrdtool graph\n\t", 
       	join("\n\t",@cmd))
 		if $ERR;       
       
       
       my ($a,$b) = $gallery_asnow ? 
       		("$tstat_rrd_cgi?gallery_show=1;gallery_asnow=0","/${file}_new.png") : 
		("$tstat_rrd_cgi?gallery_show=1;gallery_asnow=1","/$file.png") ;
       
       $text .= "<tr><th  style='border-style: none;border-color: black;border-width:1px;'>
               <a href='$a'> <img border=0 src='$b'><a/></th>
	       <td valign='top'  style='border-style: none;border-color: black;border-width:1px;'><hr> $cat <br><hr>
	       </td></tr>\n";
    }   
    close LIST;
    $text = "<i>No pictures in the gallery yet !</i><br>" unless $text;
    
    my $h3 = $gallery_asnow ? 
          "[<a href='$tstat_rrd_cgi?gallery_show=1;gallery_asnow=0'> As stored in the gallery </a>] [<b>As it is now</b>]<br>" :
          "[<b>As stored in the gallery</b>] [<a href='$tstat_rrd_cgi?gallery_show=1;gallery_asnow=1'> As it is now </a>]<br>";
          
    print returnHtml(qq{<h2> Tstat's Gallery </h2> $h3 	
        <table style="border-style: none;border-color: black;border-width:1px;">
    	$text<hr>
    	<p>});
    exit(0);
}


sub gallery_save {
my ($gallery_save,$imf,$cmdf)=@_;
#die "gallery_save(@_)", "\npar=", map { "$_ = ". url_param($_) . "\n" } url_param();
die "gallery_save(@_) should not be called" unless $gallery_save;
  
    $id = gallery_newid();
    my $text = "Updating gallery <br><hr>";
    
    if ( $system_copy == 0 ) {
       $text .= gallery_system("cp '$imf'  '$RRD_GALLERY/$id.png'");
       $text .= gallery_system("cp '$cmdf' '$RRD_GALLERY/$id.cmd'");
    } else {
       $text .= gallery_copy("$imf",  "$RRD_GALLERY/$id.png");
       # $text .= gallery_copy("$cmdf", "$RRD_GALLERY/$id.cmd");
       open ORIG, "$cmdf";
       open COPY, "> $RRD_GALLERY/$id.cmd"; 
       while(<ORIG>) {
       	  if( m/$imf/ ) {
	  print COPY "'$RRD_GALLERY/${id}_new.png'\n"
	  } else {
	  print COPY "$_";
	  }
       }
       close ORIG;
       close COPY;
    }
    open  TXT, "> $RRD_GALLERY/$id.txt";
    print TXT url_param("gallery_text");
    close TXT;
    
    print returnHtml("<h2> Tstat's Gallery </h2><hr>
    $text<hr>
    <p>
    <img src='/$RRD_GALLERY/$id.png' alt='why cant I see this $imf image?'/>
    <hr>
    Files <B>$imf</B> added to gallery as <b>$id.png</b>...<br>
    Now <a href='javascript:window.close()'>click here</a> 
    or on the above picture to close this window and go back
    or <a href='$tstat_rrd_cgi?gallery_show=1'>go to the gallery</a>
    to see what you've done!
    ");
    exit(0);
}







 
 
#   ____________________________  
#  /				\ 
# /    Global Vars.   __________/ 
# \__________________/.:nonsns:.  
# 				  

   
   %pDirection  = (
	  'NULL'   =>   '--Aggregate only--',
	  'NONE'   =>   '--Select a direction--',
    	  'both'   =>   'Incoming and outgoing',
    	    'in'   =>   'Incoming traffic only',
	    'out'  =>   'Outgoing traffic only',
	    'loc'  =>   'Local traffic only',
 	  'bothcs' =>   'Client to/from server',
 	    'c2s'  =>   'Client to server only',
 	    's2c'  =>   'Server to client only',
    );

#===============================================
#  I see your true colors... 
#-----------------------------------------------
# NAMING NOTATION
#
# (gp|d|m|l)s*{color}   
#  |  | | | |	    
#  |  | | | + slate 
#  |  | | + light   
#  |  | + medium    
#  |  + dark
#  + gnuplot	  
#

#gnuplot colors
#	   gpblue => '#0000FF',
#	   gpcyan => '#00FFFF',
#	   gpgreen => '#00FF00',
#	   gpbrown => '#A0522D',
#	   gporange => '#FFA500',
#	   gpyellow => '#FFFF00',
#	   gpred => '#FF0000',
#	   gpmagenta => '#FF00FF',
%color_tmp = ( 
   	      'brown' => '#A0522D',
#lucy in the sky with diamonds
          'msblue' => '#7B68EE',
          'sblue' => '#6A5ACD',
          'dblue' => '#00008B',
          'dsblue' => '#483D8B',
          'mblue' => '#0000CD',
          'lsblue' => '#8470FF',
          'blue' => '#0000FF',
          'lblue' => '#ADD8E6',
          'cyan' => '#00FFFF',
          'dscyan' => '#00CED1',
          'mscyan' => '#48D1CC',
          'mcyan' => '#66CDAA',
          'dcyan' => '#008B8B',
          'lcyan' => '#c0FFFF',
#tequila sunrise
          'red' => '#FF0000',
          'dred' => '#8B0000',
          'yellow' => '#FFFF00',
          'lyellow' => '#FFFFE0',
          'dyellow' => '#B8860B',
          'pyellow' => '#F4F7AA',
          'orange' => '#FFA500',
          'dorange' => '#FF8C00',
#the color of money
          'green' => '#00FF00',
          'lgreen' => '#90EE90',
          'dsgreen' => '#8FBC8F',
          'msgreen' => '#00FA9A',
          'mgreen' => '#3CB371',
          'dgreen' => '#006400',
#the ping panther
          'dpink' => '#E9967A',
          'pink' => '#FFC0CB',
          'lpink' => '#FFB6C1',
          'dspink' => '#FF1493',
          'mpink' => '#FF69B4',
          'dmagenta' => '#8B008B',
          'magenta' => '#FF00FF',
          'lmagenta' => '#FFA07A',
          'lviolet' => '#DB7093',
          'mviolet' => '#C71585',
          'violet' => '#EE82EE',
          'dviolet' => '#9400D3',
#black and white, unite
          'white' => '#FFFFFF',
          'dsgray' => '#2F4F4F',
          'lgray' => '#D3D3D3',
          'black' => '#000000',
          'gray' => '#BEBEBE',
          'dgray' => '#A9A9A9',
          'lsgray' => '#778899',
);

# duplicate all the colors:
# 'white' => '#FFFFFF' ----> 'whiteV2' => '#FFFFFE'
# 'black' => '#000000' ----> 'blackV2' => '#000001'
%color = ();
while ( my ($key, $value) = each(%color_tmp) ) {
    my $c = $value;
    $c =~ s/#//;
    # define version 2 of the color
    my ($nV2, $nV3);
    my $n = hex($c) % 16;
    if ($n < 14) {
        $nV2 = hex($c) + 1;
        $nV3 = hex($c) + 2;
    }
    else {
        $nV2 = hex($c) - 1;
        $nV3 = hex($c) - 2;
    }
    $color{$key."V3"} = sprintf("#%06x", $nV3);
    $color{$key."V2"} = sprintf("#%06x", $nV2);
    $color{$key} = $value;
}

# Default colors - these are from gnuplot:
@defColor = qw(
    dcyan  dblue   dgreen  dgray  dorange  dpink  dred  dmagenta
    lblue   lcyan  lgreen  lgray  lpink  lmagenta
    mviolet  pink blue    cyan   green   gray  orange   pink   red   magenta
    dsblue  dscyan dsgreen dsgray  dspink 
    dcyanV2  dblueV2   dgreenV2  dgrayV2  dorangeV2  dpinkV2  dredV2  dmagentaV2
    lblueV2   lcyanV2  lgreenV2  lgrayV2  lpinkV2  lmagentaV2
    mvioletV2  pinkV2 blueV2    cyanV2   greenV2   grayV2  orangeV2   pinkV2   redV2   magentaV2
    dsblueV2  dscyanV2 dsgreenV2 dsgrayV2  dspinkV2 
);
map { $_ = $color{$_} } @defColor;





#===============================================
#  description  
#-----------------------------------------------
# describe Tstat parameter in a human readable format
# automatically generated by:
#
#  /home17/mellia/LIPAR/mellia/tstat/tstat_v1.0beta/tstat -H | tr -d '#' | grep -v '^$' | awk -F'|' 'BEGIN{ print "%description = ("} (NR>1) {  printf "\t%s => \"%s\",\n", $1, $5  } END { print ");"}' > descr.txt
#
# !!! WARNING !!!
# since version 4, from splitdirection, the %description mechanism has 
# been changed. Thus, only NEWER histogram have to be appended BY HAND,
# and absolutely avoiding:
#	1) the _loc _in _out _etc postfix in the key
#	2) the "-- outgoing direction" ... in the value
#

%description = (
	chat_flow_num    => "CHAT active flows",
	msn_flow_num     => "MSN Messenger active flows",
	skype_flow_num   => "Skype flow type ",
	udp_flow_number	 => "Number of tracked UDP IN/OUT flows",
	tcp_flow_number	 => "Number of tracked TCP IN/OUT flows",
	flow_number	 => "Number of tracked TCP/UDP/RTP/RTCP flows",
	L4_flow_number	 => "Number of tracked TCP/UDP flows",
	L7_TCP_num	 => "Number of tracked TCP flows per applications",
	L7_TCP_num_c	 => "Number of tracked TCP flows per applications (cloud)",
	L7_TCP_num_nc	 => "Number of tracked TCP flows per applications (non-cloud)",
	L7_UDP_num	 => "Number of tracked UDP flows per applications",
	L7_UDP_num_c	 => "Number of tracked UDP flows per applications (cloud)",
	L7_UDP_num_nc	 => "Number of tracked UDP flows per applications (non-cloud)",
	rtcp_cl_p	 => "RTCP flow length [packet] ",
	rtcp_cl_b        => "RTCP flow length [bytes] ",
	rtcp_bt      	 => "RTCP average bitrate [bit/s] ",
	rtcp_mm_bt   	 => "RTCP associated MM flow average bitrate during interval [Kbit/s] ",
	rtcp_mm_cl_b     => "RTCP associated MM flow length [bytes] ",
	rtcp_mm_cl_p     => "RTCP associeted MM flow length [pkts] ",
	rtcp_t_lost 	 => "RTCP lost packets per flow ",
	rtcp_f_lost 	 => "RTCP fraction of lost packets during interval [%.] ",
	rtcp_lost        => "RTCP lost packets during interval",
	rtcp_dup         => "RTCP duplicated packets during interval",
 	rtcp_jitter      => "RTCP jitter during interval ",
	rtcp_rtt	 => "RTCP round trip time [ms] ",
	rtcp_avg_inter   => "RTCP interarrival delay ",
	mm_oos_p	 => "Stream number of out-of-sequence packets ",
	mm_reord_delay	 => "Stream delay of reordered packets ",
	mm_reord_p_n	 => "Stream number of reordered packets ",
	mm_burst_loss	 => "Stream burst length [packet] ",
	mm_p_late	 => "Stream probability of late packets ",
	mm_p_lost	 => "Stream probability of lost packets ",
	mm_p_dup	 => "Stream probability of duplicate packets ",
	mm_p_oos	 => "Stream probability of out-of-sequence packets ",
	mm_n_oos	 => "Stream number of out-of-sequence packets ",
	mm_avg_jitter	 => "Stream average jitter [1/10 of ms] ",
	mm_avg_ipg	 => "Stream average IPG [1/10 of ms] ",
	mm_avg_bitrate	 => "Stream bitrate [kbit/s] ",
	mm_cl_b_s	 => "Stream flow length [bytes] - short flows ",
	mm_cl_p_s	 => "Stream flow length [packet] - short flows ",
	mm_cl_b		 => "Stream flow length [bytes] - long flows",
	mm_cl_p	 	 => "Stream flow length [packet] - long flows",
	mm_tot_time_s	 => "Stream flow lifetime [ms] - short flows",
	mm_tot_time	 => "Stream flow lifetime [s] - long flows ",
	mm_rtp_pt	 => "RTP payload type ",
	mm_rtp_bitrate	 => "RTP bitrate [bit/s] ",
	mm_uni_multi	 => "Unicast/multicast flows ",
	mm_type	 	 => "Stream type ",
	udp_port_flow_dst=> "UDP destination port per flow", 	
	udp_port_dst	 => "UDP destination port packets",
	udp_tot_time	 => "UDP flow lifetime [ms]",
	udp_cl_b_l	 => "UDP flow length [byte] ",
	udp_cl_b_s	 => "UDP flow length [byte] ",
	udp_cl_p	 => "UDP flow length [packet] ",
	tcp_tot_time	 => "TCP flow lifetime [ms]",
	tcp_unnecessary_rtx_FR	 
			 => "TCP number of Unneeded FR retransmission ",
	tcp_unnecessary_rtx_RTO	 
			 => "TCP number of Unneeded RTO retransmission ",
	tcp_unnrtx_FR	 => "TCP number of Unneeded FR retransmission ",
	tcp_unnrtx_RTO	 => "TCP number of Unneeded RTO retransmission ",
	tcp_flow_control => "TCP number of Flow Control ",
	tcp_flow_ctrl    => "TCP number of Flow Control ",
	tcp_unknown	 => "TCP number of unknown anomalies",
	tcp_net_dup	 => "TCP number of Network duplicates",
	tcp_reordering	 => "TCP number of packet reordering ",
	tcp_rtx_FR	 => "TCP Number of FR Retransmission ",
	tcp_rtx_RTO	 => "TCP Number of RTO Retransmission ",
	tcp_anomalies	 => "TCP total number of anomalies ",
	tcp_rtt_cnt	 => "TCP flow RTT valid samples ",
	tcp_rtt_stdev	 => "TCP flow RTT standard deviation [ms]",
	tcp_rtt_max	 => "TCP flow maximum RTT [ms]",
	tcp_rtt_avg	 => "TCP flow average RTT [ms]",
	tcp_rtt_c_avg	 => "TCP flow average RTT [ms] (cloud)",
	tcp_rtt_nc_avg	 => "TCP flow average RTT [ms] (non-cloud)",
	tcp_rtt_min	 => "TCP flow minimum RTT [ms]",
	tcp_cl_b_l	 => "TCP flow length [byte] - coarse granularity histogram ",
	tcp_cl_b_s	 => "TCP flow length [byte] - fine granularity histogram ",
	tcp_cl_p	 => "TCP flow length [packet] ",
	tcp_cwnd	 => "TCP in-flight-size [byte]",
	tcp_win_max	 => "TCP maximum RWND [byte]",
	tcp_win_avg	 => "TCP average RWND [byte]",
	tcp_mss_used	 => "TCP negotiated MSS [byte]",
	tcp_mss_b	 => "TCP declared server MSS [byte]",
	tcp_mss_a	 => "TCP declared client MSS [byte]",
	tcp_opts_TS	 => "TCP option: Timestamp",
	tcp_opts_WS	 => "TCP option: WindowScale",
	tcp_opts_SACK	 => "TCP option: SACK",
	tcp_opts_MPTCP	 => "TCP option: MPTCP",
	tcp_port_syn_dst => "TCP destination port (SYN segments)",
	tcp_port_syn_src => "TCP source port (SYN segments)",
	tcp_port_syndst	 => "TCP destination port (SYN segments)",
	tcp_port_synsrc	 => "TCP source port (SYN segments)",
	tcp_port_dst	 => "TCP destination port",
	tcp_port_src	 => "TCP source port",
	tcp_bitrate	 => "TCP bitrate [bit/s] per applications",
	tcp_bitrate_c	 => "TCP bitrate [bit/s] per applications (cloud)",
	tcp_bitrate_nc	 => "TCP bitrate [bit/s] per applications (non-cloud)",
	udp_bitrate	 => "UDP bitrate [bit/s] per applications",
	udp_bitrate_c	 => "UDP bitrate [bit/s] per applications (cloud)",
	udp_bitrate_nc	 => "UDP bitrate [bit/s] per applications (non-cloud)",
	ip_tos	 	 => "IP type of service (TOS)",
	ip_ttl	 	 => "IP time to live (TTL)",
	ip_len	  	 => "IP packet length [byte]",
	ip_bitrate	 => "IP bitrate [bit/s]",
#	ip_bitrate_c	 => "IP bitrate [bit/s] (cloud)",
#	ip_bitrate_nc	 => "IP bitrate [bit/s] (non-cloud)",
	ip_protocol	 => "IP protocol type",
	eth_8021Q_vlanid => "802.1q VLAN id",
	p2ptv_flow_num	 => "P2P-TV Applications: Number of tracked flows",
	p2ptv_bitrate	 => "P2P-TV Applications: Bitrate [bit/s]",
        L7_HTTP_num      => "Number of tracked HTTP flows",
        L7_HTTP_num_c    => "Number of tracked HTTP flows (cloud)",
        L7_HTTP_num_nc   => "Number of tracked HTTP flows (non-cloud)",
        http_bitrate     => "HTTP bitrate [bit/s] per flow types",
        http_bitrate_c   => "HTTP bitrate [bit/s] per flow types (cloud)",
        http_bitrate_nc  => "HTTP bitrate [bit/s] per flow types (non-cloud)",
        L7_WEB_num       => "HTTP flow number",
        web_bitrate      => "HTTP bitrate [bit/s] per flow types",
        L7_TLS_num       => "TLS flow number",
        tls_bitrate      => "TLS bitrate [bit/s] per flow types",
        L7_WWW_num       => "HTTP+TLS flow number",
        www_bitrate      => "HTTP+TLS bitrate [bit/s] per flow types",
        google_flow_num  => "Google flows",
        google_bitrate   => "Google bitrate [bit/s]",
        p2p_bitrate      => "HTTP and P2P bitrate [bit/s]",
        bt_bitrate       => "Bittorrent bitrate [bit/s]",
        bt_flow_num      => "Bittorrent flows",
        L7_VIDEO_num     => "Video over HTTP flow number (Total)",
        L7_VIDEO_num_c   => "Video over HTTP flow number (cloud)",
        L7_VIDEO_num_nc  => "Video over HTTP flow number (non-cloud)",
        video_rate       => "Video over HTTP bitrate [bit/s] (Total)",
        video_rate_c     => "Video over HTTP bitrate [bit/s] (cloud)",
        video_rate_nc    => "Video over HTTP bitrate [bit/s] (non-cloud)",
        profile_flows    => "Active/Missed TCP/UDP flows",
        profile_cpu      => "CPU Load Percentage",
        profile_trash    => "Number of ignored TCP packets",
        profile_tcpdata  => "Overall TCP volume",
        tcp_thru         => "TCP throughput [kbps]",
        tcp_thru_lf      => "TCP throughput [kbps] for large flows",
        tcp_thru_lf_c    => "TCP throughput [kbps] for large flows (cloud)",
        tcp_thru_lf_nc   => "TCP throughput [kbps] for large flows (non-cloud)",
	ip_cloud	 => "IP bitrate [bit/s] (cloud)",
        L3_protocol      => "IPv4 and IPv6 packets",
        L3_bitrate       => "IPv4 and IPv6 bitrate [bit/s]",
);

#
# the following metrics DO NOT support _in _loc _out _c2s _s2c
#
%pAdirectional = (
	chat_flow_num	  => 1,  
	msn_flow_num	  => 1,  
	udp_flow_number	  => 1,  
	tcp_flow_number	  => 1, 
	flow_number	  => 1, 
	L4_flow_number	  => 1, 
	udp_port_flow_dst => 1,  #--- WARNING ---#
# 	udp_port_dst 	  => 1,  #--- WARNING ---#
# 	udp_port_flow     => 1, 
	udp_tot_time	  => 1, 
	tcp_tot_time	  => 1, 
	tcp_cwnd	  => 1, 
	tcp_win_max	  => 1, 
	tcp_win_avg	  => 1, 
	tcp_mss_used	  => 1, 
	tcp_mss_b	  => 1, 
	tcp_mss_a	  => 1, 
        tcp_interrupted   => 1, #nonsns from ftw.
	tcp_opts_TS	  => 1, 
	tcp_opts_WS	  => 1, 
	tcp_opts_SACK	  => 1, 
	tcp_opts_MPTCP	  => 1, 
	eth_8021Q_vlanid  => 1, 
        profile_flows     => 1,
        profile_cpu       => 1,
        profile_trash     => 1,
        profile_tcpdata   => 1,
);


#
# the following metrics ALSO/ONLY support _c2s _s2c
#
%pServerifiable = (
     tcp_thru		      => 1,   
     tcp_thru_lf	      => 1,   
     tcp_thru_lf_c	      => 1,   
     tcp_thru_lf_nc	      => 1,   
     tcp_unnecessary_rtx_FR   => 1,  
     tcp_unnecessary_rtx_RTO  => 1,  
     tcp_unnrtx_FR	      => 1,  
     tcp_unnrtx_RTO	      => 1,  
     tcp_flow_control	      => 1,  
     tcp_flow_ctrl	      => 1,  
     tcp_unknown	      => 1,  
     tcp_net_dup	      => 1,  
     tcp_reordering	      => 1,  
     tcp_rtx_FR 	      => 1,  
     tcp_rtx_RTO	      => 1,  
     tcp_anomalies	      => 1,  
     tcp_rtt_cnt	    => 1,  
     tcp_rtt_stdev	    => 1,  
     tcp_rtt_max	    => 1,  
     tcp_rtt_avg	    => 1,  
     tcp_rtt_c_avg	    => 1,  
     tcp_rtt_nc_avg	    => 1,  
     tcp_rtt_avg_out	    => 1, 
     tcp_rtt_min	    => 1,  
     tcp_cl_b_l 	      => 1,  
     tcp_cl_b_s 	      => 1,  
     tcp_cl_p		      => 1, 
);


foreach my $postfix (qw(loc in out c2s s2c src dst) ){
   foreach my $item (keys %description) {
       $description{"${item}_${postfix}"} = "$description{$item}"
       		unless $pAdirectional{$item}
   }
}
#%descrition2param = reverse %description;

#-----------------------------------------------

#===============================================
#  idx2value
#-----------------------------------------------
#  human readable description for tstat index values
#  this one is hand-written
#
$idx2value = {
   ip_len => {
        40   =>  [ "40 Bytes",   'orange' ], 
        1500 =>  [ "1500 Bytes", 'brown'], 
   },
   eth_8021Q_vlanid => {
        11 => [ "Zona cortile interno",  'yellow' ],
        12 => [ "Sala Consiglio",        'orange' ],
        13 => [ "Biblioteca",            'brown' ],
        14 => [ "DAUIN",                 'green' ],
        15 => [ "vlan 15",               'cyan' ],
        16 => [ "Sede Centrale - Cesit", 'blue' ],
   },
   flow_number  => {
        0 => ["TCP Flows", 'brown'], 
        1 => ["UDP Flows", 'green'],
        2 => ["RTP Flows", 'cyan'],
        3 => ["RTCP Flows",'blue'] 
   },
   L4_flow_number  => {
        0 => ["TCP Flows",'cyan'], 
        1 => ["UDP Flows",'blue'],
   },
   L7_TCP_num => {
        0  => ["HTTP",              'mviolet'],
        1  => ["RTP",               'lmagenta'],           
        2  => ["RTCP",              'lpink'],          
        3  => ["ICY",               'lgray'],           
        4  => ["RTSP",              'lgreen'],          
        5  => ["Skype E2E",         'lcyan'],    
        6  => ["Skype E2O",         'lblue'],     
        7  => ["Skype TCP",         'dmagenta'],     
        8  => ["Messenger",         'dred'],           
        9  => ["Jabber/GTalk",      'dpink'],          
        10 => ["Yahoo! Msg",        'dorange'],          
        11 => ["Emule-ED2K",        'dgray'],
        12 => ["Emule-KAD",         'mvioletV2'],#
        13 => ["Emule-KADu",        'lmagentaV2'],#
        14 => ["GNUtella",          'dgreen'],           
        15 => ["Bittorrent",        'dblue'],          
        16 => ["Kazaa",             'dcyan'],         
        17 => ["DirectConnect",     'magenta'],             
        18 => ["APPLE",             'lblueV2'], #        
        19 => ["Soulseek",          'orange'],          
        20 => ["WinMX",             'dredV2'],     #    
        21 => ["ARES",              'dpinkV2'],    #      
        22 => ["MUTE",              'dorangeV2'], #         
        23 => ["WASTE",             'dgrayV2'], #        
        24 => ["XDCC",              'dgreenV2'],#
        25 => ["SMTP",              'yellow'],
        26 => ["POP3",              'orangeV2'],
        27 => ["IMAP",              'brown'],
        28 => ["ED2K Obfuscated",   'green'],
        29 => ["PPLive",            'yellowV2'],#
        30 => ["Sopcast",           'orangeV3'],#
        31 => ["TVAnts",            'brownV2'],#
        32 => ["Skype SIG",         'greenV2'],#
        33 => ["SSL/TLS",           'cyan'],
        35 => ["Kazaa",             'dcyan'],       # Temporarly keep the old value
        37 => ["SSH",               'pyellow'],       
        38 => ["RTMP",              'brownV3'],       
        39 => ["BT-MSE/PE",         'red'],       
        46 => ["Facebook Zero",      'dgreenV2'],
        49 => ["Unclassified",      'blueV2'],       
   },
   L7_TCP_num_c => {
        0  => ["HTTP",              'mviolet'],
        1  => ["RTP",               'lmagenta'],           
        2  => ["RTCP",              'lpink'],          
        3  => ["ICY",               'lgray'],           
        4  => ["RTSP",              'lgreen'],          
        5  => ["Skype E2E",         'lcyan'],    
        6  => ["Skype E2O",         'lblue'],     
        7  => ["Skype TCP",         'dmagenta'],     
        8  => ["Messenger",         'dred'],           
        9  => ["Jabber/GTalk",      'dpink'],          
        10 => ["Yahoo! Msg",        'dorange'],          
        11 => ["Emule-ED2K",        'dgray'],
        12 => ["Emule-KAD",         'mvioletV2'],#
        13 => ["Emule-KADu",        'lmagentaV2'],#
        14 => ["GNUtella",          'dgreen'],           
        15 => ["Bittorrent",        'dblue'],          
        16 => ["Kazaa",             'dcyan'],         
        17 => ["DirectConnect",     'magenta'],             
        18 => ["APPLE",             'lblueV2'], #        
        19 => ["Soulseek",          'orange'],          
        20 => ["WinMX",             'dredV2'],     #    
        21 => ["ARES",              'dpinkV2'],    #      
        22 => ["MUTE",              'dorangeV2'], #         
        23 => ["WASTE",             'dgrayV2'], #        
        24 => ["XDCC",              'dgreenV2'],#
        25 => ["SMTP",              'yellow'],
        26 => ["POP3",              'orangeV2'],
        27 => ["IMAP",              'brown'],
        28 => ["ED2K Obfuscated",   'green'],
        29 => ["PPLive",            'yellowV2'],#
        30 => ["Sopcast",           'orangeV3'],#
        31 => ["TVAnts",            'brownV2'],#
        32 => ["Skype SIG",         'greenV2'],#
        33 => ["SSL/TLS",           'cyan'],
        35 => ["Kazaa",             'dcyan'],       # Temporarly keep the old value
        37 => ["SSH",               'pyellow'],       
        38 => ["RTMP",              'brownV3'],       
        39 => ["BT-MSE/PE",         'red'],       
        46 => ["Facebook Zero",      'dgreenV2'],
        49 => ["Unclassified",      'blueV2'],       
   },
   L7_TCP_num_nc => {
        0  => ["HTTP",              'mviolet'],
        1  => ["RTP",               'lmagenta'],           
        2  => ["RTCP",              'lpink'],          
        3  => ["ICY",               'lgray'],           
        4  => ["RTSP",              'lgreen'],          
        5  => ["Skype E2E",         'lcyan'],    
        6  => ["Skype E2O",         'lblue'],     
        7  => ["Skype TCP",         'dmagenta'],     
        8  => ["Messenger",         'dred'],           
        9  => ["Jabber/GTalk",      'dpink'],          
        10 => ["Yahoo! Msg",        'dorange'],          
        11 => ["Emule-ED2K",        'dgray'],
        12 => ["Emule-KAD",         'mvioletV2'],#
        13 => ["Emule-KADu",        'lmagentaV2'],#
        14 => ["GNUtella",          'dgreen'],           
        15 => ["Bittorrent",        'dblue'],          
        16 => ["Kazaa",             'dcyan'],         
        17 => ["DirectConnect",     'magenta'],             
        18 => ["APPLE",             'lblueV2'], #        
        19 => ["Soulseek",          'orange'],          
        20 => ["WinMX",             'dredV2'],     #    
        21 => ["ARES",              'dpinkV2'],    #      
        22 => ["MUTE",              'dorangeV2'], #         
        23 => ["WASTE",             'dgrayV2'], #        
        24 => ["XDCC",              'dgreenV2'],#
        25 => ["SMTP",              'yellow'],
        26 => ["POP3",              'orangeV2'],
        27 => ["IMAP",              'brown'],
        28 => ["ED2K Obfuscated",   'green'],
        29 => ["PPLive",            'yellowV2'],#
        30 => ["Sopcast",           'orangeV3'],#
        31 => ["TVAnts",            'brownV2'],#
        32 => ["Skype SIG",         'greenV2'],#
        33 => ["SSL/TLS",           'cyan'],
        35 => ["Kazaa",             'dcyan'],       # Temporarly keep the old value
        37 => ["SSH",               'pyellow'],       
        38 => ["RTMP",              'brownV3'],       
        39 => ["BT-MSE/PE",         'red'],       
        46 => ["Facebook Zero",      'dgreenV2'],
        49 => ["Unclassified",      'blueV2'],       
   },
   L7_UDP_num => {   	
        0  => ["HTTP",              'dscyan'], #
        1  => ["RTP",               'lblue'],           
        2  => ["RTCP",              'dmagenta'],          
        3  => ["ICY",               'red'],  #         
        4  => ["RTSP",              'pink'], #         
        5  => ["Skype E2E",         'dred'],    
        6  => ["Skype E2O",         'dpink'],     
        7  => ["Skype TCP",         'green'],#     
        8  => ["Messenger",         'cyan'],#           
        9  => ["Jabber/GTalk",      'blue'],#          
        10 => ["Yahoo! Msg",        'pinkV2'],#          
        11 => ["Emule-ED2K",        'dorange'],
        12 => ["Emule-KAD",         'dgray'],
        13 => ["Emule-KADu",        'dgreen'],
        14 => ["GNUtella",          'magenta'],           
        15 => ["Bittorrent DHT",    'dcyan'],          
        16 => ["Bittorrent uTP",    'dblue'],         
        17 => ["DirectConnect",     'redV2'],            
        18 => ["APPLE",             'dmagentaV2'], #        
        19 => ["Soulseek",          'dredV2'], #         
        20 => ["WinMX",             'dpinkV2'],  #       
        21 => ["ARES",              'dorangeV2'],  #        
        22 => ["MUTE",              'dgrayV2'],   #       
        23 => ["WASTE",             'dgreenV2'],#         
        24 => ["XDCC",              'dblueV2'],#
        25 => ["SMTP",              'dcyanV2'],#
        26 => ["POP3",              'magentaV2'],#
        27 => ["IMAP",              'redV3'],#
        29 => ["PPLive",            'yellow'],
        30 => ["Sopcast",           'orange'],
        31 => ["TVAnts",            'brown'],
        32 => ["Skype SIG",         'greenV2'],
        34 => ["KAD Obfuscated",    'cyanV2'],
        35 => ["Unclassified",      'blueV2'],     # Temporarly keep the old value      
        36 => ["DNS",               'pyellow'],       
        40 => ["MPEG2 VOD",         'red'],       
        41 => ["PPStream",          'dpink'],
        42 => ["Teredo",            'yellowV2'],
        43 => ["SIP",               'dpinkV2'],
        44 => ["DTLS",              'dorangeV2'],
        45 => ["QUIC",              'redV2'],
        49 => ["Unclassified",      'blueV3'],       
   },
   L7_UDP_num_c => {   	
        0  => ["HTTP",              'dscyan'], #
        1  => ["RTP",               'lblue'],           
        2  => ["RTCP",              'dmagenta'],          
        3  => ["ICY",               'red'],  #         
        4  => ["RTSP",              'pink'], #         
        5  => ["Skype E2E",         'dred'],    
        6  => ["Skype E2O",         'dpink'],     
        7  => ["Skype TCP",         'green'],#     
        8  => ["Messenger",         'cyan'],#           
        9  => ["Jabber/GTalk",      'blue'],#          
        10 => ["Yahoo! Msg",        'pinkV2'],#          
        11 => ["Emule-ED2K",        'dorange'],
        12 => ["Emule-KAD",         'dgray'],
        13 => ["Emule-KADu",        'dgreen'],
        14 => ["GNUtella",          'magenta'],           
        15 => ["Bittorrent DHT",    'dcyan'],          
        16 => ["Bittorrent uTP",    'dblue'],         
        17 => ["DirectConnect",     'redV2'],            
        18 => ["APPLE",             'dmagentaV2'], #        
        19 => ["Soulseek",          'dredV2'], #         
        20 => ["WinMX",             'dpinkV2'],  #       
        21 => ["ARES",              'dorangeV2'],  #        
        22 => ["MUTE",              'dgrayV2'],   #       
        23 => ["WASTE",             'dgreenV2'],#         
        24 => ["XDCC",              'dblueV2'],#
        25 => ["SMTP",              'dcyanV2'],#
        26 => ["POP3",              'magentaV2'],#
        27 => ["IMAP",              'redV3'],#
        29 => ["PPLive",            'yellow'],
        30 => ["Sopcast",           'orange'],
        31 => ["TVAnts",            'brown'],
        32 => ["Skype SIG",         'greenV2'],
        34 => ["KAD Obfuscated",    'cyanV2'],
        35 => ["Unclassified",      'blueV2'],     # Temporarly keep the old value      
        36 => ["DNS",               'pyellow'],       
        40 => ["MPEG2 VOD",         'red'],       
        41 => ["PPStream",          'dpink'],       
        42 => ["Teredo",            'yellowV2'],
        43 => ["SIP",               'dpinkV2'],
        44 => ["DTLS",              'dorangeV2'],
        45 => ["QUIC",              'redV2'],
        49 => ["Unclassified",      'blueV3'],       
   },
   L7_UDP_num_nc => {   	
        0  => ["HTTP",              'dscyan'], #
        1  => ["RTP",               'lblue'],           
        2  => ["RTCP",              'dmagenta'],          
        3  => ["ICY",               'red'],  #         
        4  => ["RTSP",              'pink'], #         
        5  => ["Skype E2E",         'dred'],    
        6  => ["Skype E2O",         'dpink'],     
        7  => ["Skype TCP",         'green'],#     
        8  => ["Messenger",         'cyan'],#           
        9  => ["Jabber/GTalk",      'blue'],#          
        10 => ["Yahoo! Msg",        'pinkV2'],#          
        11 => ["Emule-ED2K",        'dorange'],
        12 => ["Emule-KAD",         'dgray'],
        13 => ["Emule-KADu",        'dgreen'],
        14 => ["GNUtella",          'magenta'],           
        15 => ["Bittorrent DHT",    'dcyan'],          
        16 => ["Bittorrent uTP",    'dblue'],         
        17 => ["DirectConnect",     'redV2'],            
        18 => ["APPLE",             'dmagentaV2'], #        
        19 => ["Soulseek",          'dredV2'], #         
        20 => ["WinMX",             'dpinkV2'],  #       
        21 => ["ARES",              'dorangeV2'],  #        
        22 => ["MUTE",              'dgrayV2'],   #       
        23 => ["WASTE",             'dgreenV2'],#         
        24 => ["XDCC",              'dblueV2'],#
        25 => ["SMTP",              'dcyanV2'],#
        26 => ["POP3",              'magentaV2'],#
        27 => ["IMAP",              'redV3'],#
        29 => ["PPLive",            'yellow'],
        30 => ["Sopcast",           'orange'],
        31 => ["TVAnts",            'brown'],
        32 => ["Skype SIG",         'greenV2'],
        34 => ["KAD Obfuscated",    'cyanV2'],
        35 => ["Unclassified",      'blueV2'],     # Temporarly keep the old value      
        36 => ["DNS",               'pyellow'],       
        40 => ["MPEG2 VOD",         'red'],       
        41 => ["PPStream",          'dpink'],       
        42 => ["Teredo",            'yellowV2'],
        43 => ["SIP",               'dpinkV2'],
        44 => ["DTLS",              'dorangeV2'],
        45 => ["QUIC",              'redV2'],
        49 => ["Unclassified",      'blueV3'],       
   },
   ip_protocol => {
        1  => ["ICMP",  'green'], 
        6  => ["TCP",   'cyan'], 
        17 => ["UDP",   'blue'],
        41 => ["IPv6",  'orange'],
   }, 
   udp_port_dst => {   	
        53    =>["DNS",                 'dblue'],      
        67    =>["BOOTPS",              'dcyan'],      
        68    =>["BOOTPC",              'magenta'],	      
        69    =>["TFTP",                'red'],
        123   =>["NTP",                 'yellow'],
        137   =>["NETBIOS",             'orange'],
        500   =>["isakmp",              'brown'],
        4500  =>["IPsec NAT-Traversal", 'green'],
        4672  =>["eDonkey",             'cyan'],
        6346  =>["Gnutella-svc",        'blue'],
   },
   tcp_port_dst => {   	
        20   =>["FTP-DATA",             'lcyan'],	
        21   =>["FTP",                  'lblue'],	      
        22   =>["SSH",                  'dmagenta'],	      
        23   =>["telnet",               'dred'],	
        25   =>["SMTP",                 'yellow'],        
        80   =>["HTTP",                 'mviolet'],        
        110  =>["POP3",                 'dgray'],
        119  =>["NNTP",                 'dgreen'],
        143  =>["IMAP",                 'dblue'],
        443  =>["HTTPS",                'dcyan'], 	
        445  =>["Microsoft-ds",         'magenta'],  
        1214 =>["KaZaa",                'dpink'], 	
        1433 =>["Ms-SQL",               'red'],
        3389 =>["RDP",                  'orange'],
        4662 =>["eDonkey-DATA",         'pyellow'],  
        4661 =>["eDonkey-Lookup",       'brown'],
        6881 =>["BitTorrent",           'green'],	
        6699 =>["WinMX",                'cyan'], 	
        8080 =>["Squid",                'blue']
   },
   tcp_interrupted => { 
        0 => ["Completed Flow",         'cyan'],
        1 => ["Early Interrupted Flow", 'blue'],
   },
   tcp_opts_SACK => { 
        1 => ["SACK Ok",            'brown'], 
        2 => ["SACK Client Offer",  'green'], 
        3 => ["SACK Server Offer",  'cyan'], 
        4 => ["No SACK",            'blue'],
    },
   tcp_opts_WS => { 
        1 => ["Window Scale Ok",            'brown'], 
        2 => ["Window Scale Client Offer",  'green'], 
        3 => ["Window Scale Server Offer",  'cyan'], 
        4 => ["No Window Scale",            'blue'],
    },
   tcp_opts_TS => { 
        1 => ["Timestamp Ok",           'brown'], 
        2 => ["Timestamp Client Offer", 'green'], 
        3 => ["Timestamp Server Offer", 'cyan'], 
        4 => ["No Timestamp",           'blue'],
   },
   tcp_opts_MPTCP => { 
        1 => ["MPTCP Ok",            'brown'], 
        2 => ["MPTCP Client Offer",  'green'], 
        3 => ["MPTCP Server Offer",  'cyan'], 
        4 => ["No MPTCP",            'blue'],
    },
   tcp_anomalies => {
        0 => ["In Sequence",                            'dcyan'],
        1 => ["Retr. by RTO",                           'magenta'],
        2 => ["Retr. by Fast Retransmit",               'red'],
        3 => ["Network Reordering",                     'yellow'],
        4 => ["Network Duplicate",                      'orange'],
        5 => ["Flow Control (Window Probing)",          'brown'],
        6 => ["Unnecessary Retr. by RTO",               'green'],
        7 => ["Unnecessary Retr. by Fast Retransmit",   'cyan'],
        63 => ["Unknown",                               'blue'],
   },
   mm_type => {
        4 => ["RTP over UDP",       'brown'],
        6 => ["RTP over RTSP",      'green'],
        7 => ["RTP over HTTP/RTSP", 'cyan'],	
        8 => ["ICY",                'blue'],	
   },
   mm_uni_multi => {
        0 => ["Unicast",'cyan'],
        1 => ["Multicast",'blue'],
   },
   ip_bitrate => {
        0 => ["TCP",        'cyan'],
        1 => ["UDP",        'blue'],
        2 => ["ICMP",       'green'],
        3 => ["Skype E2E",  'brown'],
        4 => ["Skype E2O",  'orange'],
        5 => ["Skype TCP",  'yellow'],
   },
   ip_bitrate_c => {
        0 => ["TCP",        'cyan'],
        1 => ["UDP",        'blue'],
        2 => ["ICMP",       'green'],
        3 => ["Skype E2E",  'brown'],
        4 => ["Skype E2O",  'orange'],
        5 => ["Skype TCP",  'yellow'],
   },
   ip_bitrate_nc => {
        0 => ["TCP",        'cyan'],
        1 => ["UDP",        'blue'],
        2 => ["ICMP",       'green'],
        3 => ["Skype E2E",  'brown'],
        4 => ["Skype E2O",  'orange'],
        5 => ["Skype TCP",  'yellow'],
   },
   mm_rtp_bitrate => {
        0 => ["RTP over TCP",'cyan'],
        1 => ["RTP over UDP",'blue'],
   },
   mm_rtp_pt => {
        97 => ["dynamic video",     'magenta'],
        96 => ["dynamic video",     'red'],
        33 => ["MP2T",              'yellow'],
        32 => ["MPV",               'orange'],
        31 => ["H261",              'brown'],
        14 => ["MPA",               'green'],
        8  => ["ITU G.711 a-law",   'cyan'],
        0  => ["ITU G.711 u-law",   'blue'],
   },
#   skype_flow_num => {
#	0 => 'Not Skype',
#	1 => 'Voice over TCP',
#	2 => 'First RTCP',
#	3 => 'RTP',
#	4 => 'RTCP',
#	5 => 'Voice over UDP - E2E',
#	6  => 'Voice over UDP - skypeout',
#	7  => 'SKYPE SIG',
#   },
   skype_flow_num => {
        5 => ["Voice over UDP - End2End",   'brown'],
        6  => ["Voice over UDP - SkypeOut", 'green'],
        7  => ["Skype over TCP",            'cyan'],
        32 => ["Signalling over UDP",       'blue'],
   },
   msn_flow_num => {
        0 => ["Active chat session number",     'cyan'],
        1 => ["Active presence session number", 'blue'],
   },
   chat_flow_num => {
        0 => ["MSN chat session number",        'yellow'],
        1 => ["MSN presence session number",    'orange'],
        2 => ["Jabber chat session number",     'brown'],
        3 => ["Jabber presence session number", 'green'],
        4 => ["YAHOO chat session number",      'cyan'],
        5 => ["YAHOO presence session number",  'blue'],
   },
#   chat_flow_num => {
#	0 => 'MSN chat session number',
#	1 => 'MSN presence session number',
#	2 => 'Jabber chat session number',
#	3 => 'Jabber presence session number',
#	4 => 'YAHOO chat session number',
#	5 => 'YAHOO presence session number',
#   },
   tcp_bitrate => {   	
        0  => ["HTTP",              'mviolet'],
        1  => ["RTP",               'lmagenta'],            
        2  => ["RTCP",              'lpink'],          
        3  => ["ICY",               'lgray'],           
        4  => ["RTSP",              'lgreen'],          
        5  => ["Skype E2E",         'lcyan'],  #  
        6  => ["Skype E2O",         'lblue'], #     
        7  => ["Skype TCP",         'dmagenta'],     
        8  => ["Messenger",         'dred'],           
        9  => ["Jabber/GTalk",      'dpink'],          
        10 => ["Yahoo! Msg",        'dorange'],          
        11 => ["Emule-ED2K",        'dgray'],
        12 => ["Emule-KAD",         'mvioletV2'],#
        13 => ["Emule-KADu",        'lmagentaV2'],#
        14 => ["GNUtella",          'dgreen'],           
        15 => ["Bittorrent",        'dblue'],          
        16 => ["Kazaa",             'dcyan'],         
        17 => ["DirectConnect",     'magenta'],             
        18 => ["APPLE",             'lblueV2'], #        
        19 => ["Soulseek",          'orange'],          
        20 => ["WinMX",             'dredV2'],     #    
        21 => ["ARES",              'dpinkV2'],    #      
        22 => ["MUTE",              'dorangeV2'], #         
        23 => ["WASTE",             'dgrayV2'], #        
        24 => ["XDCC",              'dgreenV2'],#
        25 => ["SMTP",              'yellow'],
        26 => ["POP3",              'orangeV2'],
        27 => ["IMAP",              'brown'],
        28 => ["ED2K Obfuscated",   'green'],
        29 => ["PPLive",            'yellowV2'],#
        30 => ["Sopcast",           'orangeV3'],#
        31 => ["TVAnts",            'brownV2'],#
        32 => ["Skype SIG",         'greenV2'],#
        33 => ["SSL/TLS",           'cyan'],
        35 => ["Kazaa",      'blue'],       # Temporarly keep the old value
        37 => ["SSH",               'pyellow'],
        38 => ["RTMP",              'brownV3'],
        39 => ["BT-MSE/PE",         'red'],
        46 => ["Facebook Zero",      'dgreenV2'],
        49 => ["Unclassified",      'blueV2'],
#        0  => ["HTTP",'dscyan'],
#        1  => ["RTP",'dsblue'],           
#        2  => ["RTCP",'magenta'],          
#        3  => ["ICY",'red'],           
#        4  => ["RTSP",'pink'],          
#        5  => ["Skype E2E",'orange'],    
#        6  => ["Skype E2O",'gray'],     
#        7  => ["Skype TCP",'green'],     
#        8  => ["Messenger",'cyan'],           
#        9  => ["Jabber/GTalk",'blue'],          
#        10 => ["Yahoo! Msg",'pink'],          
#        11 => ["Emule-ED2K",'mviolet'],
#        12 => ["Emule-KAD",'lmagenta'],
#        13 => ["Emule-KADu",'lred'],
#        14 => ["GNUtella",'lpink'],           
#        15 => ["Bittorrent",'lgray'],          
#        16 => ["Kazaa",'lgreen'],         
#        17 => ["DirectConnect",'lcyan'],            
#        18 => ["APPLE",'lblue'],         
#        19 => ["Soulseek",'dmagenta'],          
#        20 => ["WinMX",'dred'],         
#        21 => ["ARES",'dpink'],          
#        22 => ["MUTE",'dorange'],          
#        23 => ["WASTE",'dgray'],         
#        24 => ["XDCC",'dgreen'],
#        25 => ["SMTP",'dblue'],
#        26 => ["POP3",'dcyan'],
#        27 => ["IMAP",'magenta'],
#        28 => ["ED2K Obfuscated",'red'],
#	29 => ["PPLive",'yellow'],
#	30 => ["Sopcast",'orange'],
#	31 => ["TVAnts",'brown'],#
#	32 => ["Skype SIG",'green'],#
#        33 => ["SSL/TLS",'cyan'],
#        35 => ["Unclassified",'blue'],   # Temporarly keep the old value    
#        37 => ["SSH",'pyellow'],       
#        49 => ["Unclassified",'blue'],       
   },
   tcp_bitrate_c => {   	
        0  => ["HTTP",              'mviolet'],
        1  => ["RTP",               'lmagenta'],            
        2  => ["RTCP",              'lpink'],          
        3  => ["ICY",               'lgray'],           
        4  => ["RTSP",              'lgreen'],          
        5  => ["Skype E2E",         'lcyan'],  #  
        6  => ["Skype E2O",         'lblue'], #     
        7  => ["Skype TCP",         'dmagenta'],     
        8  => ["Messenger",         'dred'],           
        9  => ["Jabber/GTalk",      'dpink'],          
        10 => ["Yahoo! Msg",        'dorange'],          
        11 => ["Emule-ED2K",        'dgray'],
        12 => ["Emule-KAD",         'mvioletV2'],#
        13 => ["Emule-KADu",        'lmagentaV2'],#
        14 => ["GNUtella",          'dgreen'],           
        15 => ["Bittorrent",        'dblue'],          
        16 => ["Kazaa",             'dcyan'],         
        17 => ["DirectConnect",     'magenta'],             
        18 => ["APPLE",             'lblueV2'], #        
        19 => ["Soulseek",          'orange'],          
        20 => ["WinMX",             'dredV2'],     #    
        21 => ["ARES",              'dpinkV2'],    #      
        22 => ["MUTE",              'dorangeV2'], #         
        23 => ["WASTE",             'dgrayV2'], #        
        24 => ["XDCC",              'dgreenV2'],#
        25 => ["SMTP",              'yellow'],
        26 => ["POP3",              'orangeV2'],
        27 => ["IMAP",              'brown'],
        28 => ["ED2K Obfuscated",   'green'],
        29 => ["PPLive",            'yellowV2'],#
        30 => ["Sopcast",           'orangeV3'],#
        31 => ["TVAnts",            'brownV2'],#
        32 => ["Skype SIG",         'greenV2'],#
        33 => ["SSL/TLS",           'cyan'],
        35 => ["Kazaa",      'blue'],       # Temporarly keep the old value
        37 => ["SSH",               'pyellow'],
        38 => ["RTMP",              'brownV3'],
        39 => ["BT-MSE/PE",         'red'],
        46 => ["Facebook Zero",      'dgreenV2'],
        49 => ["Unclassified",      'blueV2'],
#        0  => ["HTTP",'dscyan'],
#        1  => ["RTP",'dsblue'],           
#        2  => ["RTCP",'magenta'],          
#        3  => ["ICY",'red'],           
#        4  => ["RTSP",'pink'],          
#        5  => ["Skype E2E",'orange'],    
#        6  => ["Skype E2O",'gray'],     
#        7  => ["Skype TCP",'green'],     
#        8  => ["Messenger",'cyan'],           
#        9  => ["Jabber/GTalk",'blue'],          
#        10 => ["Yahoo! Msg",'pink'],          
#        11 => ["Emule-ED2K",'mviolet'],
#        12 => ["Emule-KAD",'lmagenta'],
#        13 => ["Emule-KADu",'lred'],
#        14 => ["GNUtella",'lpink'],           
#        15 => ["Bittorrent",'lgray'],          
#        16 => ["Kazaa",'lgreen'],         
#        17 => ["DirectConnect",'lcyan'],            
#        18 => ["APPLE",'lblue'],         
#        19 => ["Soulseek",'dmagenta'],          
#        20 => ["WinMX",'dred'],         
#        21 => ["ARES",'dpink'],          
#        22 => ["MUTE",'dorange'],          
#        23 => ["WASTE",'dgray'],         
#        24 => ["XDCC",'dgreen'],
#        25 => ["SMTP",'dblue'],
#        26 => ["POP3",'dcyan'],
#        27 => ["IMAP",'magenta'],
#        28 => ["ED2K Obfuscated",'red'],
#	29 => ["PPLive",'yellow'],
#	30 => ["Sopcast",'orange'],
#	31 => ["TVAnts",'brown'],#
#	32 => ["Skype SIG",'green'],#
#        33 => ["SSL/TLS",'cyan'],
#        35 => ["Unclassified",'blue'],   # Temporarly keep the old value    
#        37 => ["SSH",'pyellow'],       
#        49 => ["Unclassified",'blue'],       
   },
   tcp_bitrate_nc => {   	
        0  => ["HTTP",              'mviolet'],
        1  => ["RTP",               'lmagenta'],            
        2  => ["RTCP",              'lpink'],          
        3  => ["ICY",               'lgray'],           
        4  => ["RTSP",              'lgreen'],          
        5  => ["Skype E2E",         'lcyan'],  #  
        6  => ["Skype E2O",         'lblue'], #     
        7  => ["Skype TCP",         'dmagenta'],     
        8  => ["Messenger",         'dred'],           
        9  => ["Jabber/GTalk",      'dpink'],          
        10 => ["Yahoo! Msg",        'dorange'],          
        11 => ["Emule-ED2K",        'dgray'],
        12 => ["Emule-KAD",         'mvioletV2'],#
        13 => ["Emule-KADu",        'lmagentaV2'],#
        14 => ["GNUtella",          'dgreen'],           
        15 => ["Bittorrent",        'dblue'],          
        16 => ["Kazaa",             'dcyan'],         
        17 => ["DirectConnect",     'magenta'],             
        18 => ["APPLE",             'lblueV2'], #        
        19 => ["Soulseek",          'orange'],          
        20 => ["WinMX",             'dredV2'],     #    
        21 => ["ARES",              'dpinkV2'],    #      
        22 => ["MUTE",              'dorangeV2'], #         
        23 => ["WASTE",             'dgrayV2'], #        
        24 => ["XDCC",              'dgreenV2'],#
        25 => ["SMTP",              'yellow'],
        26 => ["POP3",              'orangeV2'],
        27 => ["IMAP",              'brown'],
        28 => ["ED2K Obfuscated",   'green'],
        29 => ["PPLive",            'yellowV2'],#
        30 => ["Sopcast",           'orangeV3'],#
        31 => ["TVAnts",            'brownV2'],#
        32 => ["Skype SIG",         'greenV2'],#
        33 => ["SSL/TLS",           'cyan'],
        35 => ["Kazaa",      'blue'],       # Temporarly keep the old value
        37 => ["SSH",               'pyellow'],
        38 => ["RTMP",              'brownV3'],
        39 => ["BT-MSE/PE",         'red'],
        46 => ["Facebook Zero",      'dgreenV2'],
        49 => ["Unclassified",      'blueV2'],
#        0  => ["HTTP",'dscyan'],
#        1  => ["RTP",'dsblue'],           
#        2  => ["RTCP",'magenta'],          
#        3  => ["ICY",'red'],           
#        4  => ["RTSP",'pink'],          
#        5  => ["Skype E2E",'orange'],    
#        6  => ["Skype E2O",'gray'],     
#        7  => ["Skype TCP",'green'],     
#        8  => ["Messenger",'cyan'],           
#        9  => ["Jabber/GTalk",'blue'],          
#        10 => ["Yahoo! Msg",'pink'],          
#        11 => ["Emule-ED2K",'mviolet'],
#        12 => ["Emule-KAD",'lmagenta'],
#        13 => ["Emule-KADu",'lred'],
#        14 => ["GNUtella",'lpink'],           
#        15 => ["Bittorrent",'lgray'],          
#        16 => ["Kazaa",'lgreen'],         
#        17 => ["DirectConnect",'lcyan'],            
#        18 => ["APPLE",'lblue'],         
#        19 => ["Soulseek",'dmagenta'],          
#        20 => ["WinMX",'dred'],         
#        21 => ["ARES",'dpink'],          
#        22 => ["MUTE",'dorange'],          
#        23 => ["WASTE",'dgray'],         
#        24 => ["XDCC",'dgreen'],
#        25 => ["SMTP",'dblue'],
#        26 => ["POP3",'dcyan'],
#        27 => ["IMAP",'magenta'],
#        28 => ["ED2K Obfuscated",'red'],
#	29 => ["PPLive",'yellow'],
#	30 => ["Sopcast",'orange'],
#	31 => ["TVAnts",'brown'],#
#	32 => ["Skype SIG",'green'],#
#        33 => ["SSL/TLS",'cyan'],
#        35 => ["Unclassified",'blue'],   # Temporarly keep the old value    
#        37 => ["SSH",'pyellow'],       
#        49 => ["Unclassified",'blue'],       
   },
   udp_bitrate => {   	
        0  => ["HTTP",              'dscyan'], #
        1  => ["RTP",               'lblue'],           
        2  => ["RTCP",              'dmagenta'],          
        3  => ["ICY",               'red'],  #         
        4  => ["RTSP",              'pink'], #         
        5  => ["Skype E2E",         'dred'],    
        6  => ["Skype E2O",         'dpink'],     
        7  => ["Skype TCP",         'green'],#     
        8  => ["Messenger",         'cyan'],#           
        9  => ["Jabber/GTalk",      'blue'],#          
        10 => ["Yahoo! Msg",        'pinkV2'],#          
        11 => ["Emule-ED2K",        'dorange'],
        12 => ["Emule-KAD",         'dgray'],
        13 => ["Emule-KADu",        'dgreen'],
        14 => ["GNUtella",          'magenta'],           
        15 => ["Bittorrent DHT",    'dcyan'],          
        16 => ["Bittorrent uTP",    'dblue'],         
        17 => ["DirectConnect",     'redV2'],            
        18 => ["APPLE",             'dmagentaV2'], #        
        19 => ["Soulseek",          'dredV2'], #         
        20 => ["WinMX",             'dpinkV2'],  #       
        21 => ["ARES",              'dorangeV2'],  #        
        22 => ["MUTE",              'dgrayV2'],   #       
        23 => ["WASTE",             'dgreenV2'],#         
        24 => ["XDCC",              'dblueV2'],#
        25 => ["SMTP",              'dcyanV2'],#
        26 => ["POP3",              'magentaV2'],#
        27 => ["IMAP",              'redV3'],#
        29 => ["PPLive",            'yellow'],
        30 => ["Sopcast",           'orange'],
        31 => ["TVAnts",            'brown'],
        32 => ["Skype SIG",         'greenV2'],
        34 => ["KAD Obfuscated",    'cyanV2'],
        35 => ["Kazaa",             'blueV2'],     # Temporarly keep the old value      
        36 => ["DNS",               'pyellow'],       
        40 => ["MPEG2 VOD",         'red'],       
        41 => ["PPStream",          'dpink'],       
        42 => ["Teredo",            'yellowV2'],
        43 => ["SIP",               'dpinkV2'],
        44 => ["DTLS",              'dorangeV2'],
        45 => ["QUIC",              'redV2'],
        49 => ["Unclassified",      'blueV3'],       
#        0  => ["HTTP",'dscyan'],
#        1  => ["RTP",'dsblue'],           
#        2  => ["RTCP",'magenta'],          
#        3  => ["ICY",'red'],           
#        4  => ["RTSP",'pink'],          
#        5  => ["Skype E2E",'orange'],    
#        6  => ["Skype E2O",'gray'],     
#        7  => ["Skype TCP",'green'],     
#        8  => ["Messenger",'cyan'],           
#        9  => ["Jabber/GTalk",'blue'],          
#        10 => ["Yahoo! Msg",'pink'],          
#        11 => ["Emule-ED2K",'mviolet'],
#        12 => ["Emule-KAD",'lmagenta'],
#        13 => ["Emule-KADu",'lpink'],
#        14 => ["GNUtella",'lgray'],           
#        15 => ["Bittorrent",'lgreen'],          
#        16 => ["Kazaa",'lcyan'],         
#        17 => ["DirectConnect",'lblue'],            
#        18 => ["APPLE",'dmagenta'],         
#        19 => ["Soulseek",'dred'],          
#        20 => ["WinMX",'dpink'],         
#        21 => ["ARES",'dorange'],          
#        22 => ["MUTE",'dgray'],          
#        23 => ["WASTE",'dgreen'],         
#        24 => ["XDCC",'dblue'],
#        25 => ["SMTP",'dcyan'],
#        26 => ["POP3",'magenta'],
#        27 => ["IMAP",'red'],
#	29 => ["PPLive",'yellow'],
#	30 => ["Sopcast",'orange'],
#	31 => ["TVAnts",'brown'],
#	32 => ["Skype SIG",'green'],
#        34 => ["KAD Obfuscated",'cyan'],
#        35 => ["Unclassified",'blue'],   # Temporarly keep the old value        
#        36 => ["DNS",'pyellow'],       
#        49 => ["Unclassified",'blue'],       
   },
   udp_bitrate_c => {   	
        0  => ["HTTP",              'dscyan'], #
        1  => ["RTP",               'lblue'],           
        2  => ["RTCP",              'dmagenta'],          
        3  => ["ICY",               'red'],  #         
        4  => ["RTSP",              'pink'], #         
        5  => ["Skype E2E",         'dred'],    
        6  => ["Skype E2O",         'dpink'],     
        7  => ["Skype TCP",         'green'],#     
        8  => ["Messenger",         'cyan'],#           
        9  => ["Jabber/GTalk",      'blue'],#          
        10 => ["Yahoo! Msg",        'pinkV2'],#          
        11 => ["Emule-ED2K",        'dorange'],
        12 => ["Emule-KAD",         'dgray'],
        13 => ["Emule-KADu",        'dgreen'],
        14 => ["GNUtella",          'magenta'],           
        15 => ["Bittorrent DHT",    'dcyan'],          
        16 => ["Bittorrent uTP",    'dblue'],         
        17 => ["DirectConnect",     'redV2'],            
        18 => ["APPLE",             'dmagentaV2'], #        
        19 => ["Soulseek",          'dredV2'], #         
        20 => ["WinMX",             'dpinkV2'],  #       
        21 => ["ARES",              'dorangeV2'],  #        
        22 => ["MUTE",              'dgrayV2'],   #       
        23 => ["WASTE",             'dgreenV2'],#         
        24 => ["XDCC",              'dblueV2'],#
        25 => ["SMTP",              'dcyanV2'],#
        26 => ["POP3",              'magentaV2'],#
        27 => ["IMAP",              'redV3'],#
        29 => ["PPLive",            'yellow'],
        30 => ["Sopcast",           'orange'],
        31 => ["TVAnts",            'brown'],
        32 => ["Skype SIG",         'greenV2'],
        34 => ["KAD Obfuscated",    'cyanV2'],
        35 => ["Kazaa",             'blueV2'],     # Temporarly keep the old value      
        36 => ["DNS",               'pyellow'],       
        40 => ["MPEG2 VOD",         'red'],       
        41 => ["PPStream",          'dpink'],       
        42 => ["Teredo",            'yellowV2'],
        43 => ["SIP",               'dpinkV2'],
        44 => ["DTLS",              'dorangeV2'],
        45 => ["QUIC",              'redV2'],
        49 => ["Unclassified",      'blueV3'],       
#        0  => ["HTTP",'dscyan'],
#        1  => ["RTP",'dsblue'],           
#        2  => ["RTCP",'magenta'],          
#        3  => ["ICY",'red'],           
#        4  => ["RTSP",'pink'],          
#        5  => ["Skype E2E",'orange'],    
#        6  => ["Skype E2O",'gray'],     
#        7  => ["Skype TCP",'green'],     
#        8  => ["Messenger",'cyan'],           
#        9  => ["Jabber/GTalk",'blue'],          
#        10 => ["Yahoo! Msg",'pink'],          
#        11 => ["Emule-ED2K",'mviolet'],
#        12 => ["Emule-KAD",'lmagenta'],
#        13 => ["Emule-KADu",'lpink'],
#        14 => ["GNUtella",'lgray'],           
#        15 => ["Bittorrent",'lgreen'],          
#        16 => ["Kazaa",'lcyan'],         
#        17 => ["DirectConnect",'lblue'],            
#        18 => ["APPLE",'dmagenta'],         
#        19 => ["Soulseek",'dred'],          
#        20 => ["WinMX",'dpink'],         
#        21 => ["ARES",'dorange'],          
#        22 => ["MUTE",'dgray'],          
#        23 => ["WASTE",'dgreen'],         
#        24 => ["XDCC",'dblue'],
#        25 => ["SMTP",'dcyan'],
#        26 => ["POP3",'magenta'],
#        27 => ["IMAP",'red'],
#	29 => ["PPLive",'yellow'],
#	30 => ["Sopcast",'orange'],
#	31 => ["TVAnts",'brown'],
#	32 => ["Skype SIG",'green'],
#        34 => ["KAD Obfuscated",'cyan'],
#        35 => ["Unclassified",'blue'],   # Temporarly keep the old value        
#        36 => ["DNS",'pyellow'],       
#        49 => ["Unclassified",'blue'],       
   },
   udp_bitrate_nc => {   	
        0  => ["HTTP",              'dscyan'], #
        1  => ["RTP",               'lblue'],           
        2  => ["RTCP",              'dmagenta'],          
        3  => ["ICY",               'red'],  #         
        4  => ["RTSP",              'pink'], #         
        5  => ["Skype E2E",         'dred'],    
        6  => ["Skype E2O",         'dpink'],     
        7  => ["Skype TCP",         'green'],#     
        8  => ["Messenger",         'cyan'],#           
        9  => ["Jabber/GTalk",      'blue'],#          
        10 => ["Yahoo! Msg",        'pinkV2'],#          
        11 => ["Emule-ED2K",        'dorange'],
        12 => ["Emule-KAD",         'dgray'],
        13 => ["Emule-KADu",        'dgreen'],
        14 => ["GNUtella",          'magenta'],           
        15 => ["Bittorrent DHT",    'dcyan'],          
        16 => ["Bittorrent uTP",    'dblue'],         
        17 => ["DirectConnect",     'redV2'],            
        18 => ["APPLE",             'dmagentaV2'], #        
        19 => ["Soulseek",          'dredV2'], #         
        20 => ["WinMX",             'dpinkV2'],  #       
        21 => ["ARES",              'dorangeV2'],  #        
        22 => ["MUTE",              'dgrayV2'],   #       
        23 => ["WASTE",             'dgreenV2'],#         
        24 => ["XDCC",              'dblueV2'],#
        25 => ["SMTP",              'dcyanV2'],#
        26 => ["POP3",              'magentaV2'],#
        27 => ["IMAP",              'redV3'],#
        29 => ["PPLive",            'yellow'],
        30 => ["Sopcast",           'orange'],
        31 => ["TVAnts",            'brown'],
        32 => ["Skype SIG",         'greenV2'],
        34 => ["KAD Obfuscated",    'cyanV2'],
        35 => ["Kazaa",             'blueV2'],     # Temporarly keep the old value      
        36 => ["DNS",               'pyellow'],       
        40 => ["MPEG2 VOD",         'red'],       
        41 => ["PPStream",          'dpink'],       
        42 => ["Teredo",            'yellowV2'],
        43 => ["SIP",               'dpinkV2'],
        44 => ["DTLS",              'dorangeV2'],
        45 => ["QUIC",              'redV2'],
        49 => ["Unclassified",      'blueV3'],       
#        0  => ["HTTP",'dscyan'],
#        1  => ["RTP",'dsblue'],           
#        2  => ["RTCP",'magenta'],          
#        3  => ["ICY",'red'],           
#        4  => ["RTSP",'pink'],          
#        5  => ["Skype E2E",'orange'],    
#        6  => ["Skype E2O",'gray'],     
#        7  => ["Skype TCP",'green'],     
#        8  => ["Messenger",'cyan'],           
#        9  => ["Jabber/GTalk",'blue'],          
#        10 => ["Yahoo! Msg",'pink'],          
#        11 => ["Emule-ED2K",'mviolet'],
#        12 => ["Emule-KAD",'lmagenta'],
#        13 => ["Emule-KADu",'lpink'],
#        14 => ["GNUtella",'lgray'],           
#        15 => ["Bittorrent",'lgreen'],          
#        16 => ["Kazaa",'lcyan'],         
#        17 => ["DirectConnect",'lblue'],            
#        18 => ["APPLE",'dmagenta'],         
#        19 => ["Soulseek",'dred'],          
#        20 => ["WinMX",'dpink'],         
#        21 => ["ARES",'dorange'],          
#        22 => ["MUTE",'dgray'],          
#        23 => ["WASTE",'dgreen'],         
#        24 => ["XDCC",'dblue'],
#        25 => ["SMTP",'dcyan'],
#        26 => ["POP3",'magenta'],
#        27 => ["IMAP",'red'],
#	29 => ["PPLive",'yellow'],
#	30 => ["Sopcast",'orange'],
#	31 => ["TVAnts",'brown'],
#	32 => ["Skype SIG",'green'],
#        34 => ["KAD Obfuscated",'cyan'],
#        35 => ["Unclassified",'blue'],   # Temporarly keep the old value        
#        36 => ["DNS",'pyellow'],       
#        49 => ["Unclassified",'blue'],       
   },
   p2ptv_flow_num => {
        29 => ["PPLive",    'green'],
        30 => ["Sopcast",   'cyan'],
        31 => ["TVAnts",    'blue'],
        41 => ["PPStream",  'msblue'],
   },
   p2ptv_bitrate => {
        29 => ["PPLive",    'green'],
        30 => ["Sopcast",   'cyan'],
        31 => ["TVAnts",    'blue'],
        41 => ["PPStream",  'msblue'],
   },
   L7_HTTP_num => {
         0 => ["GET",               'mviolet'],
         1 => ["POST",              'yellow'],
         2 => ["MSN",               'cyan'],
         3 => ["RTMPT",             'brown'],
         4 => ["YouTube Video",     'orange'],
         5 => ["Video Content",      'green'],
         6 => ["Vimeo",             'red'],
         7 => ["Wikipedia",         'blue'],
         8 => ["RapidShare",        'pink'],
         9 => ["Netload",        'dblue'],
         10 => ["Facebook",         'magenta'],
         11 => ["Web Ads",          'dgray'],
         12 => ["Flickr",           'dred'],
         13 => ["Google Maps",      'dgreen'],
         14 => ["Netflix",  'msblue'],
         15 => ["YouTube Site",     'redV2'],
         16 => ["Social",           'greenV2'],
         17 => ["Other Video",      'brownV2'],
         18 => ["Mediafire",        'cyanV2'],
         19 => ["Hotfile.com",      'yellowV2'],
         20 => ["Storage.to",       'mvioletV2'],
   },
   L7_HTTP_num_c => {
         0 => ["GET",               'mviolet'],
         1 => ["POST",              'yellow'],
         2 => ["MSN",               'cyan'],
         3 => ["RTMPT",             'brown'],
         4 => ["YouTube Video",     'orange'],
         5 => ["Video Content",      'green'],
         6 => ["Vimeo",             'red'],
         7 => ["Wikipedia",         'blue'],
         8 => ["RapidShare",        'pink'],
         9 => ["Netload",        'dblue'],
         10 => ["Facebook",         'magenta'],
         11 => ["Web Ads",          'dgray'],
         12 => ["Flickr",           'dred'],
         13 => ["Google Maps",      'dgreen'],
         14 => ["Netflix",  'msblue'],
         15 => ["YouTube Site",     'redV2'],
         16 => ["Social",           'greenV2'],
         17 => ["Other Video",      'brownV2'],
         18 => ["Mediafire",        'cyanV2'],
         19 => ["Hotfile.com",      'yellowV2'],
         20 => ["Storage.to",       'mvioletV2'],
   },
   L7_HTTP_num_nc => {
         0 => ["GET",               'mviolet'],
         1 => ["POST",              'yellow'],
         2 => ["MSN",               'cyan'],
         3 => ["RTMPT",             'brown'],
         4 => ["YouTube Video",     'orange'],
         5 => ["Video Content",      'green'],
         6 => ["Vimeo",             'red'],
         7 => ["Wikipedia",         'blue'],
         8 => ["RapidShare",        'pink'],
         9 => ["Netload",        'dblue'],
         10 => ["Facebook",         'magenta'],
         11 => ["Web Ads",          'dgray'],
         12 => ["Flickr",           'dred'],
         13 => ["Google Maps",      'dgreen'],
         14 => ["Netflix",  'msblue'],
         15 => ["YouTube Site",     'redV2'],
         16 => ["Social",           'greenV2'],
         17 => ["Other Video",      'brownV2'],
         18 => ["Mediafire",        'cyanV2'],
         19 => ["Hotfile.com",      'yellowV2'],
         20 => ["Storage.to",       'mvioletV2'],
   },
   http_bitrate => {
         0 => ["GET",               'mviolet'],
         1 => ["POST",              'yellow'],
         2 => ["MSN",               'cyan'],
         3 => ["RTMPT",             'brown'],
         4 => ["YouTube",           'orange'],
         5 => ["Video Content",      'green'],
         6 => ["Vimeo",             'red'],
         7 => ["Wikipedia",         'blue'],
         8 => ["RapidShare",        'pink'],
         9 => ["Netload",        'dblue'],
         10 => ["Facebook",         'magenta'],
         11 => ["Web Ads",          'dgray'],
         12 => ["Flickr",           'dred'],
         13 => ["Google Maps",      'dgreen'],
         14 => ["Netflix",  'msblue'],
         15 => ["YouTube Site",     'redV2'],
         16 => ["Social",           'greenV2'],
         17 => ["Other Video",      'brownV2'],
         18 => ["Mediafire",        'cyanV2'],
         19 => ["Hotfile.com",      'yellowV2'],
         20 => ["Storage.to",       'mvioletV2']
   },
   http_bitrate_c => {
         0 => ["GET",               'mviolet'],
         1 => ["POST",              'yellow'],
         2 => ["MSN",               'cyan'],
         3 => ["RTMPT",             'brown'],
         4 => ["YouTube",           'orange'],
         5 => ["Video Content",      'green'],
         6 => ["Vimeo",             'red'],
         7 => ["Wikipedia",         'blue'],
         8 => ["RapidShare",        'pink'],
         9 => ["Netload",        'dblue'],
         10 => ["Facebook",         'magenta'],
         11 => ["Web Ads",          'dgray'],
         12 => ["Flickr",           'dred'],
         13 => ["Google Maps",      'dgreen'],
         14 => ["Netflix",  'msblue'],
         15 => ["YouTube Site",     'redV2'],
         16 => ["Social",           'greenV2'],
         17 => ["Other Video",      'brownV2'],
         18 => ["Mediafire",        'cyanV2'],
         19 => ["Hotfile.com",      'yellowV2'],
         20 => ["Storage.to",       'mvioletV2'],
   },
   http_bitrate_nc => {
         0 => ["GET",               'mviolet'],
         1 => ["POST",              'yellow'],
         2 => ["MSN",               'cyan'],
         3 => ["RTMPT",             'brown'],
         4 => ["YouTube",           'orange'],
         5 => ["Video Content",      'green'],
         6 => ["Vimeo",             'red'],
         7 => ["Wikipedia",         'blue'],
         8 => ["RapidShare",        'pink'],
         9 => ["Netload",        'dblue'],
         10 => ["Facebook",         'magenta'],
         11 => ["Web Ads",          'dgray'],
         12 => ["Flickr",           'dred'],
         13 => ["Google Maps",      'dgreen'],
         14 => ["Netflix",  'msblue'],
         15 => ["YouTube Site",     'redV2'],
         16 => ["Social",           'greenV2'],
         17 => ["Other Video",      'brownV2'],
         18 => ["Mediafire",        'cyanV2'],
         19 => ["Hotfile.com",      'yellowV2'],
         20 => ["Storage.to",       'mvioletV2'],
   },
   L7_WEB_num => {
         0 => ["GET",               'mviolet', 0],
         1 => ["POST",              'yellow', 5],
         2 => ["1-Click Download",  'dblue', 4],
         3 => ["YouTube",           'orange', 2],
         4 => ["Other Videos", 'dgreen', 1],
         5 => ["Social Networks",   'magenta', 6],
         6 => ["Other",             'blue', 8],
         7 => ["Netflix",             'red', 3],
         8 => ["SSL/TLS",           'lblue', 7]
   },
   web_bitrate => {
         0 => ["GET",               'mviolet', 0],
         1 => ["POST",              'yellow', 5],
         2 => ["1-Click Download",  'dblue', 4],
         3 => ["YouTube",           'orange', 2],
         4 => ["Other Videos", 'dgreen', 1],
         5 => ["Social Networks",   'magenta', 6],
         6 => ["Other",             'blue', 8],
         7 => ["Netflix",             'red', 3],
         8 => ["SSL/TLS",           'lblue', 7],
   },
   L7_TLS_num => {
         0 => ["Other",               'lblue', 7],
         1 => ["Google",              'yellow', 1],
         2 => ["YouTube",  'dblue', 0],
         3 => ["Facebook",           'orange', 2],
         4 => ["Netflix", 'dgreen', 5],
         5 => ["Dropbox",   'magenta', 3],
         6 => ["Microsoft",             'blue', 4],
         7 => ["Apple",             'pink', 6],
   },
   tls_bitrate => {
         0 => ["Other",               'lblue', 7],
         1 => ["Google",              'yellow', 1],
         2 => ["YouTube",  'dblue', 0],
         3 => ["Facebook",           'orange', 2],
         4 => ["Netflix", 'dgreen', 5],
         5 => ["Dropbox",   'magenta', 3],
         6 => ["Microsoft",             'blue', 4],
         7 => ["Apple",             'pink', 6],
   },
   L7_WWW_num => {
         0 => ["GET",               'mviolet', 0],
         1 => ["POST",              'yellow', 1],
         7 => ["Google (TLS)",              'cyan', 2],
         2 => ["YouTube",           'brown', 3],
         8 => ["YouTube (TLS)",  'orange', 4],
         5 => ["Netflix",             'dred', 5],
        10 => ["Netflix (TLS)", 'redV2', 6],
         3 => ["Video Streams", 'dgreen', 7],
         9 => ["Facebook (TLS)",           'magenta', 8],
        14 => ["Facebook (Zero)",           'dmagenta', 9],
        11 => ["Dropbox (TLS)",   'yellowV2', 10],
        12 => ["Microsoft (TLS)",             'msblue', 11],
        13 => ["Apple (TLS)",             'pink', 12],
         4 => ["Other",             'blue', 13],
         6 => ["Other (TLS)",               'lblue', 14],
   },
   www_bitrate => {
         0 => ["GET",               'mviolet', 0],
         1 => ["POST",              'yellow', 1],
         7 => ["Google (TLS)",              'cyan', 2],
         2 => ["YouTube",           'brown', 3],
         8 => ["YouTube (TLS)",  'orange', 4],
         5 => ["Netflix",             'dred', 5],
        10 => ["Netflix (TLS)", 'redV2', 6],
         3 => ["Video Streams", 'dgreen', 7],
         9 => ["Facebook (TLS)",           'magenta', 8],
        14 => ["Facebook (Zero)",           'dmagenta', 9],
        11 => ["Dropbox (TLS)",   'yellowV2', 10],
        12 => ["Microsoft (TLS)",             'msblue', 11],
        13 => ["Apple (TLS)",             'pink', 12],
         4 => ["Other",             'blue', 13],
         6 => ["Other (TLS)",               'lblue', 14],
   },
   google_flow_num => {
         0 => ["QUIC (UDP)",               'mviolet', 2],
         2 => ["Google (TLS)",              'cyan', 3],
         1 => ["YouTube",           'blue', 1],
         3 => ["YouTube (TLS)",  'orange', 0],
   },
   google_bitrate => {
         0 => ["QUIC (UDP)",               'mviolet', 2],
         2 => ["Google (TLS)",              'cyan', 3],
         1 => ["YouTube",           'blue', 1],
         3 => ["YouTube (TLS)",  'orange', 0],
   },
   p2p_bitrate => {
         0 => ["HTTP",               'mviolet', 0],
         1 => ["SSL/TLS",            'orange', 1],
         2 => ["Emule-ED2K",  'dgreen', 2],
         3 => ["ED2K Obfuscated",           'green', 3],
         4 => ["Bittorrent", 'dblue', 4],
         5 => ["BT-MSE/PE",   'cyan', 5],
         6 => ["Bittorrent uTP (UDP)",             'blue', 6],
   },
   bt_flow_num => {
         0 => ["BT-MSE/PE (TCP)",         'red',1],
         1 => ["BitTorrent (TCP)",               'cyan',2],
         2 => ["uTP (UDP)",           'orange',3],
         3 => ["DHT (UDP)",           'blue',4],
         4 => ["Teredo (IPv6 over UDP)", 'dblue',0],
   },
   bt_bitrate => {
         0 => ["BT-MSE/PE (TCP)",         'red',1],
         1 => ["BitTorrent (TCP)",               'cyan',2],
         2 => ["uTP (UDP)",           'orange',3],
         3 => ["DHT (UDP)",           'blue',4],
         4 => ["Teredo (IPv6 over UDP)", 'dblue',0],
   },
   L7_VIDEO_num => {
         1 => ["FLV",               'mviolet',0],
         2 => ["MP4",              'orange',1],
         3 => ["AVI",               'dgreen',2],
         4 => ["WMV",             'brown',3],
         5 => ["MPEG",           'yellow',4],
         6 => ["WEBM",      'green',5],
         7 => ["3GPP",             'dgray',6],
         8 => ["OGG",         'magenta',7],
         9 => ["QuickTime",        'pyellow',8],
         10 => ["ASF",        'pink',9],
         11 => ["Unknown",         'blue',10],
         12 => ["HLS",       'red',12],
         13 => ["NFF",       'cyan',11],
   },
   L7_VIDEO_num_c => {
         1 => ["FLV",               'mviolet',0],
         2 => ["MP4",              'orange',1],
         3 => ["AVI",               'dgreen',2],
         4 => ["WMV",             'brown',3],
         5 => ["MPEG",           'yellow',4],
         6 => ["WEBM",      'green',5],
         7 => ["3GPP",             'dgray',6],
         8 => ["OGG",         'magenta',7],
         9 => ["QuickTime",        'pyellow',8],
         10 => ["ASF",        'pink',9],
         11 => ["Unknown",         'blue',10],
         12 => ["HLS",       'red',12],
         13 => ["NFF",       'cyan',11],
   },
   L7_VIDEO_num_nc => {
         1 => ["FLV",               'mviolet',0],
         2 => ["MP4",              'orange',1],
         3 => ["AVI",               'dgreen',2],
         4 => ["WMV",             'brown',3],
         5 => ["MPEG",           'yellow',4],
         6 => ["WEBM",      'green',5],
         7 => ["3GPP",             'dgray',6],
         8 => ["OGG",         'magenta',7],
         9 => ["QuickTime",        'pyellow',8],
         10 => ["ASF",        'pink',9],
         11 => ["Unknown",         'blue',10],
         12 => ["HLS",       'red',12],
         13 => ["NFF",       'cyan',11],
   },
   video_rate => {
         1 => ["FLV",               'mviolet',0],
         2 => ["MP4",              'orange',1],
         3 => ["AVI",               'dgreen',2],
         4 => ["WMV",             'brown',3],
         5 => ["MPEG",           'yellow',4],
         6 => ["WEBM",      'green',5],
         7 => ["3GPP",             'dgray',6],
         8 => ["OGG",         'magenta',7],
         9 => ["QuickTime",        'pyellow',8],
         10 => ["ASF",        'pink',9],
         11 => ["Unknown",         'blue',10],
         12 => ["HLS",       'red',12],
         13 => ["NFF",       'cyan',11],
   },
   video_rate_c => {
         1 => ["FLV",               'mviolet',0],
         2 => ["MP4",              'orange',1],
         3 => ["AVI",               'dgreen',2],
         4 => ["WMV",             'brown',3],
         5 => ["MPEG",           'yellow',4],
         6 => ["WEBM",      'green',5],
         7 => ["3GPP",             'dgray',6],
         8 => ["OGG",         'magenta',7],
         9 => ["QuickTime",        'pyellow',8],
         10 => ["ASF",        'pink',9],
         11 => ["Unknown",         'blue',10],
         12 => ["HLS",       'red',12],
         13 => ["NFF",       'cyan',11],
   },
   video_rate_nc => {
         1 => ["FLV",               'mviolet',0],
         2 => ["MP4",              'orange',1],
         3 => ["AVI",               'dgreen',2],
         4 => ["WMV",             'brown',3],
         5 => ["MPEG",           'yellow',4],
         6 => ["WEBM",      'green',5],
         7 => ["3GPP",             'dgray',6],
         8 => ["OGG",         'magenta',7],
         9 => ["QuickTime",        'pyellow',8],
         10 => ["ASF",        'pink',9],
         11 => ["Unknown",         'blue',10],
         12 => ["HLS",       'red',12],
         13 => ["NFF",       'cyan',11],
   },
   ip_cloud => {
        0 => ["TCP (cloud)",   'blue',4], 
        1 => ["TCP (non-cloud)",   'cyan',2],
        2 => ["UDP (cloud)",   'orange',3], 
        3 => ["UDP (non-cloud)",   'mviolet',1],
   },
   L3_protocol => {
        0 => ["TCP (IPv4)",   'cyan',3], 
        1 => ["UDP (IPv4)",   'blue',4],
        2 => ["Others (IPv4)",   'orange',5], 
        3 => ["TCP (IPv6)",   'mviolet',0],
        4 => ["UDP (IPv6)",   'dgreen',1], 
        5 => ["Other (IPv6)",   'magrenta',2],
   },
   L3_bitrate => {
        0 => ["TCP (IPv4)",   'cyan',3], 
        1 => ["UDP (IPv4)",   'blue',4],
        2 => ["Others (IPv4)",   'orange',5], 
        3 => ["TCP (IPv6)",   'mviolet',0],
        4 => ["UDP (IPv6)",   'dgreen',1], 
        5 => ["Other (IPv6)",   'magrenta',2],
   },
   profile_flows  => {
        0 => ["Missed UDP Flows",   'brown'], 
        1 => ["Active UDP Flows",   'green'],
        2 => ["Missed TCP Flows",   'cyan'], 
        3 => ["Active TCP Flows",   'blue'],
   },
   profile_cpu  => {
        0 => ["Maximum Overall CPU",    'red'], 
        1 => ["Average User CPU",       'green'],
        2 => ["Average System CPU",     'blue'],
   },
   profile_trash  => {
        0 => ["Ignored TCP Packets",    'blue'], 
   },
   profile_tcpdata  => {
        0 => ["Received TCP Mbytes",    'green',1], 
        1 => ["Missed TCP Mbytes",       'blue',2],
   },
};  



$idx2value->{tcp_port_syndst} = $idx2value->{tcp_port_dst};
$idx2value->{udp_port_flow}   = $idx2value->{udp_port_flow_dst} = $idx2value->{udp_port_dst};


#--- append _in and _out and _loc ---
map { 
  $idx2value->{"${_}_loc"} = $idx2value->{"${_}_out"} = $idx2value->{"${_}_in"} = $idx2value->{$_} 
} keys %{$idx2value};

# ---Check---
#	use Data::Dumper;
#	print Dumper( \$idx2value );
#	print $idx2value->{tcp_anomalies_out}{0};
#	exit;


#print labelOf("udp_bitrate_out",'idx48'),"\n";
#print colorOf("udp_bitrate_out",'idx48',5),"\n";

#exit;

main();
