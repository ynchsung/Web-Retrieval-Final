<!DOCTYPE html>

<html lang="en-US">
    <head>
        <title>Homepage</title>
        <meta charset="utf-8" />
        <meta name="Homepage" content="width=device-width, initial-scale=1" />
        <link rel="stylesheet" href="http://www.csie.ntu.edu.tw/~b01902011/css/styles.css" />
        <link rel="stylesheet" href="css/homepage.css" />
        <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.css" />
        <link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap-theme.css" />
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
        <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/js/bootstrap.js"></script>
    </head>
    <body>
        <nav class="navbar navbar-inverse navbar-fixed-top">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="http://www.csie.ntu.edu.tw/~b01902011/">Yen-Chieh</a>
                </div>
                <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                    <ul class="nav navbar-nav">
                        <li><a href="http://www.csie.ntu.edu.tw/~b01902011/info.php">Info</a></li>
                        <li><a href="http://www.csie.ntu.edu.tw/~b01902011/subject.php">Subject</a></li>
                        <li class="dropdown">
                            <a class="dropdown-toggle" href="#" data-toggle="dropdown">Material <span class="caret"></span></a>
                            <ul class="dropdown-menu">
<?php
    $s1 = shell_exec("ls material/");
    $tok = strtok($s1, " \n");
    while( $tok !== false )
    {
        $tmp = ucfirst($tok);
        if( $tmp == "Cpp" ) $tmp = "C++";
        echo "<li><a href=\"http://www.csie.ntu.edu.tw/~b01902011/material.php?type=".$tok."\">".$tmp."</a></li>\n";
        $tok = strtok(" \n");
    }
?>
                            </ul>
                        </li>
                        <li><a href="http://www.csie.ntu.edu.tw/~b01902011/data.php">Data</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        <div style="clear:both; width:100%; height:70px;"></div>
        <div class="container">
            <div class="jumbotron profile">
                <img src="images/profile.jpg" alt="Profile" style="float:right; width:15%; height:15%;" title="Profile" />
                <h1>Yen-Chieh Sung</h1>
                <a style="color:silver; font-size:150%; text-decoration:underline;" title="b01902011" href="http://www.csie.ntu.edu.tw/~b01902011/">http://www.csie.ntu.edu.tw/~b01902011/</a>
            </div>
            <center>
                <h1>~ Welcome to my website ~</h1>
                <img src="images/home.jpg" alt="home" style="display:inline-block; width:40%; height:40%;" />
            </center>
        </div>
        <div class="footer-blank"></div>
        <div class="navbar navbar-inverse navbar-fixed-bottom" id="footer">
            <p class="navbar-text" style="float:None;">Copyright &copy; NTUCSIE 2015</p>
        </div>
    </body>
</html>
