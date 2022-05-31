const music = require("./music.js")

const { Client, Intents } = require("discord.js");
const client = new Client({
  intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES]
});
const config = require("../config.json");

client.on("ready", () => {
  console.log("I am ready!");
});

let prefix = "$";
client.on("messageCreate", (message) => {
  // Exit and stop if the prefix is not there or if user is a bot
  if (!message.content.startsWith(prefix)) return;
  if (message.author.bot) return;

  if (message.content.startsWith(`${prefix}ping`)) {
    message.channel.send("pong!");
  } else if (message.content.startsWith(`${prefix}join`)) {
    music.check_permissions(message)
  }

});


client.login(config.token);