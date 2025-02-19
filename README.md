### English version

# D&D and Pafthfinder Initiative Tracker
A short python script for console, used to help manage and track initiative and combat in Dungeons&Dragons, Pathfinder and other similar systems. Re-written with Pathfinder 2e in mind.

# Usage
An example of a valid document can be found in the repository under the name `Hero.csv` and `BadGuy.csv`. To start the script with the characters to load as arguements, one such example may be `python DnDInitiativeTracker.py Hero.csv BadGuy.csv`. I don't currently support saving to anywhere except where main script is running, but eventually might. When I update my code for home use I might remember to update this too.
After reading the initiatives and rolling the necessary ones (if Init field is left blank such as Hero), the list will be sorted and the program will print it with an arrow showing the current turn, and prompt the user to choose actions to perform. These available actions are:
+ **Add** - Add another entity to the list. The program will prompt to insert a name, an initiative score or modifier, a dexterity score and an HP score. Before adding the entity, the program will prompt for confirmation.
+ **Damage** - Apply damage to someone. The program will prompt to select an entity via their turn order ID (note that it counts from 0), and then insert an amount of damage. If the user wishes to heal the entity instead, they can insert a negative score. Example: after selecting ID 8, the user types 6, dealing 6 damage to the entity with ID 8. If the user instead types -6, the entity will be healed by 6 HP.
+ **Conditon** - Edit the condtions imposed on character.
+ **Next** - Go to next turn. This will make the arrow indicating the turn advance by one.
+ **Edit** - Change the initiative value for a player; reorder the list.
+ **Quit** - Exit from the tracker. If the user confirms, the program quits. **No data is saved.**
+ **Remove** - Remove someone from the list. The program prompts to select the ID of an entity, and then ask for confirmation. If the user confirms, the entity is removed from the turn order.
+ **Save** - Save an initiative file. The program will save a file with the given name in the current directory with the current turn order. The file is formatted such that it can be loaded from the program. If no name is provided, the default name is `Initiatives.txt`.
+ **Turn** - Set a specific turn. The Program will prompt to insert the ID of an entity, and the turn tracker will jump to that entity.

# License
This code is lincensed under the MIT License.
