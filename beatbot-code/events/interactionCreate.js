const config = require("../config.json");

module.exports = {
    name: "interactionCreate", 
    on: true, 
    async execute(interaction, client) {
        if(!interaction.isCommand()){ return; }
        
        const command = client.commands.get(interaction.commandName);
        
        if (!command) return;

        try {            
            await command.execute(interaction);
        } catch (error) {
            console.error(error);
            await interaction.reply({ content: 'There was an error while executing this slash command!', ephemeral: true });
        }
    },
};