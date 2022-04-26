<div align="center">
  
  # BeatBot
  
  BeatBot is a discord music bot, that plays songs over discord calls.
  Inspired by Rhythm and Groovy.
  
</div>
  
# Installation
## *Step 1: Create a Discord bot application*

In order to interact with Discord, a Bot application has to be made. This is a [guide](https://discordpy.readthedocs.io/en/stable/discord.html) explaing how to make a bot and add it to a server. This is also where you would set a custom profile picture. **Save your token** this will be needed for later steps.

## *Step 2: Clone this repository*
Clone this repository somewhere. To clone this repo,  run this command in your terminal.

```git clone https://github.com/KagazzIe/Discord-BeatBot```

## *Step 3: Insert your token*

Paste the token received when creating the Discord bot application into the file [token.txt](token.txt)

## *Step 4: Begin the application*

Beatbot can be run in multiple different ways.


### *Run locally*

Pip install all of the python packages in [PythonPackages](/beatbot-code/pythonPackages)

Install [ffmpeg](https://www.ffmpeg.org/download.html), and add it to the [path](https://windowsloop.com/install-ffmpeg-windows-10/)

Run Main.py and your bot should start.
    

### *Run in a local container*
Run the [Dockerfile](/beatbot-code/Dockerfile) to create a docker continer.

Then run the docker container on your local machine and the bot should start running.


### *Run in a container on the cloud*
Link an AWS account to the CDK with ```aws configure```

By default, running this will create a EC2 t3a.small instance on the linked AWS account. There is no current way for a user change this, other than altering the code in .

Run ```cdk synthesize``` to build the aws stacks

Run ```cdk bootstrap``` then ```cdk deploy --all``` to push the stacks into AWS. This will take a few minutes to complete.