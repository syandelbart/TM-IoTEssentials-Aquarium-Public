<!DOCTYPE html>
<html>
      
<head>
    <title>
        How to call PHP function
        on the click of a Button ?
    </title>
    <style>
        input {
            height:100px;
            font-size:30px;
            width:100vw;
            max-width:500px;
            background-color:blue;
            color:white;
            margin:20px;
            border-radius:20px;
        }
    </style>
</head>
  
<body style="text-align:center;">
      
    <h1 style="color:green;">
        GeeksforGeeks
    </h1>
      
    <h4>
        Control panel for RaspberriPI
    </h4>
  
    <?php
        //You have to first create a folder named "webserver" in your home directory with the appropriate permissions
        $HOME_DIR = "pi";

        error_reporting(E_ALL);
        if(isset($_POST['button1'])) {
            //If button one is pressed, create a file with the time at which the lamp should go off
            $myfile = fopen("/home/$HOME_DIR/webserver/time", "w") or die("Unable to open file!");
            $txt = time() + 60 * 15;
            fwrite($myfile, $txt);
            fclose($myfile);
        }
        if(isset($_POST['button2'])) {
            if(is_writable("/home/$HOME_DIR/webserver/time")) {
                unlink("/home/$HOME_DIR/webserver/time");
            }


            $command = escapeshellcmd('gpio -g write 26 1');
            $output = shell_exec($command);
            echo "<pre>$output</pre>";
        }
    ?>
      
    <form method="post">
        <input type="submit" name="button1"
                value="Start light for 15 minutes"/>
          
        <input type="submit" name="button2"
                value="Stop light"/>
    </form>
</body>
  
</html>