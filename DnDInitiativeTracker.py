import random
import sys
import os
import pandas as pd
import readline

def rlinput(prompt, prefill=''):
    def strtobool (val):
        """Convert a string representation of truth to true (1) or false (0).
        True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
        are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
        'val' is anything else.
        """
        val = val.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1'):
            return 1
        elif val in ('n', 'no', 'f', 'false', 'off', '0'):
            return 0
        else:
            raise ValueError("invalid truth value %r" % (val,))
    readline.set_startup_hook(lambda: readline.insert_text(str(prefill)))
    try:
        if isinstance(prefill, str):
            return input(prompt)
        elif isinstance(prefill, bool):
            return bool(strtobool(input(prompt)))
        elif prefill.is_integer():
            return int(input(prompt))
    finally:
        readline.set_startup_hook()

def InitSort(Data):
    Data = Data.sort_values(by=['Init', 'Mod'], ascending = [False, False], ignore_index = True)
    return Data

def AddToInit(Data):
    Name = input('Name: ')
    Init = input('Init (leave blank to generate from Mod): ')
    Mod = input('Mod: ')
    Init = (random.randint(1,20)+int(Mod)) if (Init == '') else int(Init)
    HP = input('HP: ')
    print('Do you want to add the following entity to the initiative list? [yN]\n\tName: ', Name, '\n\tInit: ', Init, '\n\tMod: ', Mod, '\n\tHP: ', HP, sep='')
    YN = input()
    if YN.lower() in ('yes', 'true', 't', 'y', '1' ,''):
        Data = Data._append({'Turn': ' ', 'Name': Name, 'Init': Init, 'Mod': Mod, 'HP': HP, 'Conditions': ConditionManager()}, ignore_index=True)
        return InitSort(Data)
    else:
        return Data

def EditInit(Data, CurrTurn):
    CurrPlayer = Data['Name'][CurrTurn]
    inp = input('Change initiative of which ID [Blank for Current]: ')
    if inp == '':
        inp = str(CurrTurn)
    if inp.isnumeric():
        ID = int(inp)
        if ID < len(Data['Name']):
            name =  Data['Name'][ID]
            print('You selected ', name, ', what do you want to change their Initiative to?', sep='')
            inp2 = input('New Initiative: ')
            if inp2.isnumeric():
                Data['Init'][ID] = int(inp2)
                Data = InitSort(Data)
                CurrTurn = Data['Name'].loc[lambda x: x==name].index.tolist()[0]
                print(Data)
    return Data, CurrTurn

def ApplyDamage(Data, CurrTurn):
    inp = input('Who do you wish to apply damage to? (Insert ID from the tracker list)  [Blank for Current]')
    if inp == '':
        inp = str(CurrTurn)
    if inp.isnumeric():
        ID = int(inp)
        if ID < len(Data['Name']):
            print('You selected ', Data['Name'][ID], ', if you chose the wrong character apply 0 damage.', sep='')
            DMG = int(input('How much damage to apply? (Negative values will result in healing) '))
            Data['HP'][ID] = int(Data['HP'][ID]) - DMG
    return Data

def NextTurn(Data, CurrTurn):
    for ind in Data.index:
        Data.loc[ind,'Turn'] = ' '
    # Apply any conditions that trigger at the end of the turn
    Data.loc[CurrTurn, 'Conditions'].turnEnd()
    Data.loc[CurrTurn, 'Conditions'].sustainCheck(Data.loc[CurrTurn,'Name'])
    CurrTurn = CurrTurn+1 if CurrTurn+1 < len(Data['Name']) else 0
    Data.loc[CurrTurn,'Turn'] = '==>'
    Data.loc[CurrTurn, 'Conditions'].turnStart()
    return Data, CurrTurn

def SetTurn(Data, CurrTurn):
    currTrunInitial = CurrTurn.copy()
    inp = input('Insert new turn ID ')
    if inp.isnumeric():
        NewTurn = int(inp)
        if NewTurn < len(Data['Turn']):
            for ind in Data.index:
                Data['Turn'][ind] = ' '
            Data['Turn'][NewTurn] = '==>'
            CurrTurn = NewTurn
        else:
            input('Invalid selection, please retry. Hit any key to proceed. ')
    return Data, currTrunInitial

def RemoveFromInit(Data, CurrTurn):
    inp = input('Who do you wish to remove? (Insert ID from the tracker list, invalid choice will result in return to action selection) ')
    if inp.isnumeric():
        ID = int()
        if ID < len(Data['Name']):
            print('You selected ', Data['Name'][ID], ', do you really wish to remove them? [yN]', sep='', end=' ')
            YN = input()
            if YN.lower() in ('yes', 'true', 't', 'y', '1'):
                Data = Data.drop(ID)
                Data = Data.reset_index(drop=True)
                if ID < CurrTurn:
                    CurrTurn = CurrTurn-1
                elif ID == CurrTurn:
                    if CurrTurn < len(Data['Turn'])-1:
                        Data['Turn'][ID] = '==>'
                    else:
                        CurrTurn = 0
                        Data['Turn'][0] = '==>'
    return Data, CurrTurn

def SaveToFile(Data):
    YN = input('Are you sure you want to save all active characters. Old will be overwritten.')
    if YN.lower() in ('yes', 'true', 't', 'y', '1', ''):
        for ind in range(len(Data)):
            filename = Data.loc[ind, "Name"]
            if os.path.exists(f'{filename}.csv'):
                os.remove(f'{filename}.csv')
            df1 = Data.drop(['Turn', 'Conditions'], axis= 'columns').loc[[ind]]
            df2 = Data.loc[ind, 'Conditions'].returnFullTable()
            for d in [df1, df2]:
                d.to_csv(f'{filename}.csv', mode='a', index=False)
        input('Characters saved. Hit any key to proceed. ')
    pass

def ConditionMenu(Data, CurrTurn):
    inp = input('Who do you wish to apply a condition to? (Insert ID from the tracker list) \nMultiple comma sparated IDs will have a condition applied to each [Blank for Current]:')
    if inp == '':
        inp = str(CurrTurn)
    if inp.isnumeric():
        ID = int(inp)
        if ID < len(Data['Name']):
            while True:
                #Clear window
                os.system('cls' if os.name=='nt' else 'clear')
                #Print initiatives
                if len(Data.loc[ID, 'Conditions'].returnFullTable()) > 0:
                    print(Data.loc[ID, 'Conditions'].returnFullTable())
                Instruction = input(
'\nAvailable actions:\n \
\t[aA] Add - Add Condition to the list;\n \
\t[rR] Remove - remove someone from the list;\n \
\t[eE] Edit - Change a Condition;\n \
\t[qQ] Quit - Exit from the Conditions screen.\n \
Choose an action '                  )
                if Instruction.lower() in ('a', 'e', 'q', 'r'):
                    #Add Condition
                    if Instruction.lower() == 'a':
                        Data.loc[ID, 'Conditions'].addConditions()
                    #Remove Condition
                    elif Instruction.lower() == 'r':
                        Data.loc[ID, 'Conditions'].removeCondition()
                    #Edit Condition
                    elif Instruction.lower() == 'e':
                        Data.loc[ID, 'Conditions'].editCondition()
                    #Quit Conditions
                    elif Instruction.lower() == 'q':
                        YN = input('Are you finished editing Conditions? [yN] ')
                        if YN.lower() in ('yes', 'true', 't', 'y', '1', ''):
                            break
                        else:
                            continue
                else:
                    input('Invalid selection, retry. Hit any key to proceed. ')
                    continue
    else:
        try:
            IDs = inp.split(',')
            AddCon = input('Do you wish to add a condition? [y/yes/1/True]: ')
            if AddCon.lower() in ('yes', 'true', 't', 'y', '1' ,''):
                Effect = input('Effect Name: ')
                Duration = input('Effect Duration [an integer will decrement at the end of every round automatically]: ')
                if Duration.isnumeric(): # for short duration effects, we can check for integer in this field, and count it down automatically
                    Duration = int(Duration)
                    AoEoT = bool(input('Do you want to be prompted on changing this condition on End of Turn [Start of turn will be asked if you say no]\n[Blank for False]: '))
                    if AoEoT == False:
                        AoSoT = bool(input('Do you want to be prompted on changing this condition on Start of Turn [Blank for False]: '))
                    else:
                        AoSoT = False
                else:
                    Duration = str(Duration)
                    AoEoT = False
                    AoSoT = False
                Sustain = bool(input('Does the effect need to be sustained every turn [Blank for False]: '))
                print('Do you want to add the following entity to the condition list? [yN]\n\tEffect: ', Effect, '\n\tDuration: ', Duration, sep='')
                YN = input()
                if YN.lower() in ('yes', 'true', 't', 'y', '1' ,''):
                    for ind in IDs:
                        ID = int(ind)
                        Data.loc[ID, 'Conditions'].insertCondition( Effect, Duration, AoEoT, AoSoT, Sustain)
                else:
                    pass
        except:
            pass
    return Data

class ConditionManager:
    def __init__(self, initialDF = None):
        if initialDF is not None:
            self.condTable = initialDF
        else:
            self.condTable = pd.DataFrame(columns=['Effect', 'Duration', 'Alter on Start of Turn', 'Alter on End of Turn', 'Sustain'])
    def addConditions(self):
        AddCon = input('Do you wish to add a condition? [y/yes/1/True]: ')
        if AddCon.lower() in ('yes', 'true', 't', 'y', '1' ,''):
            Effect = input('Effect Name: ')
            Duration = input('Effect Duration [an integer will decrement at the end of every round automatically]: ')
            if Duration.isnumeric(): # for short duration effects, we can check for integer in this field, and count it down automatically
                Duration = int(Duration)
                AoEoT = bool(input('Do you want to be prompted on changing this condition on End of Turn [Start of turn will be asked if you say no]\n[Blank for False]: '))
                if AoEoT == False:
                    AoSoT = bool(input('Do you want to be prompted on changing this condition on Start of Turn [Blank for False]: '))
                else:
                    AoSoT = False
            else:
                Duration = str(Duration)
                AoEoT = False
                AoSoT = False
            Sustain = bool(input('Does the effect need to be sustained every turn [Blank for False]: '))
            print('Do you want to add the following entity to the condition list? [yN]\n\tEffect: ', Effect, '\n\tDuration: ', Duration, sep='')
            YN = input()
            if YN.lower() in ('yes', 'true', 't', 'y', '1' ,''):
                self.condTable = self.condTable._append({'Effect': Effect, 'Duration': Duration, 'Alter on Start of Turn': AoSoT, 'Alter on End of Turn': AoEoT, 'Sustain': Sustain}, ignore_index=True)
        else:
            pass
    def insertCondition(self, Effect, Duration, AoEoT, AoSoT, Sustain):
        #useful to add condition to many characters
        self.condTable = self.condTable._append({'Effect': Effect, 'Duration': Duration, 'Alter on Start of Turn': AoSoT, 'Alter on End of Turn': AoEoT, 'Sustain': Sustain}, ignore_index=True)
    def editCondition(self,ind = None):
        if ind == None:
            ind = int(input('Edit which effect, by index: '))
        self.condTable.loc[ind,"Effect"] = rlinput('Alter the Effect Name: ', prefill = self.condTable.loc[ind,"Effect"])
        self.condTable.loc[ind,"Duration"] = rlinput('Alter the Duration to: ', prefill = self.condTable.loc[ind,"Duration"])
        self.condTable.loc[ind,"Alter on End of Turn"] = rlinput('Alter the End of Turn trigger to: ', prefill = bool(self.condTable.loc[ind,"Alter on End of Turn"]))
        self.condTable.loc[ind,"Alter on Start of Turn"] = rlinput('Alter the Start of Turn trigger to: ', prefill = bool(self.condTable.loc[ind,"Alter on Start of Turn"]))
        self.condTable.loc[ind,"Sustain"] = rlinput('Alter the Sustain flag to: ', prefill = bool(self.condTable.loc[ind,"Sustain"]))
    def removeCondition(self, ind = None):
        if ind == None:
            ind = int(input('Delete which effect, by index: '))
        if isinstance(ind, list):
            self.condTable = self.condTable.drop(ind)
            self.condTable = self.condTable.reset_index(drop=True)
        elif ind.is_integer(): #unlike isinstance, is_intager doesn't discrimiate numpy formats
            self.condTable = self.condTable.drop(int(ind))
            self.condTable = self.condTable.reset_index(drop=True)

    def turnStart(self):
        rowsToDelete = []
        for ind in self.condTable.index:
            if self.condTable.loc[ind,'Alter on Start of Turn']:
                try:
                    self.condTable.loc[ind,'Duration'] = int(self.condTable.loc[ind,'Duration']) - 1
                except ValueError:
                    # prompt with text input to alter condition
                    delCon = input(f'{self.condTable.loc[ind,"Effect"]} is due to be modified on turn end, do you simply want to delete it? [y/yes/1/True]: ')
                    if delCon.lower() in ('yes', 'true', 't', 'y', '1'):
                        rowsToDelete.append(ind)
                    else:
                        self.editCondition(ind)
        rowsToDelete2 = self.condTable.index[self.condTable['Duration'] == 0].tolist()
        rowsToDelete = rowsToDelete + rowsToDelete2
        rowsToDelete = list(set(rowsToDelete))
        if len(rowsToDelete) > 0:
            self.removeCondition(rowsToDelete)
    def turnEnd(self):
        rowsToDelete = []
        for ind in self.condTable.index:
            if self.condTable.loc[ind,'Alter on End of Turn']:
                try:
                    self.condTable.loc[ind,'Duration'] = int(self.condTable.loc[ind,'Duration']) - 1
                except ValueError:
                    # prompt with text input to alter condition
                    delCon = input(f'{self.condTable.loc[ind,"Effect"]} is due to be modified on turn end, do you simply want to delete it? [y/yes/1/True]: ')
                    if delCon.lower() in ('yes', 'true', 't', 'y', '1'):
                        rowsToDelete.append(ind)
                    else:
                        self.editCondition(ind)
        rowsToDelete2 = self.condTable.index[self.condTable['Duration'] == 0].tolist()
        rowsToDelete = rowsToDelete + rowsToDelete2
        rowsToDelete = list(set(rowsToDelete))
        if len(rowsToDelete) > 0:
            self.removeCondition(rowsToDelete)
    def sustainCheck(self, name):
        rowsToDelete = []
        for ind in self.condTable.index:
            if self.condTable.loc[ind,'Sustain']:
                # prompt to ask if effect was sustained
                sustained = input(f'Did {name} sustain {self.condTable.loc[ind,"Effect"]} ? [y/yes/1/True]: ')
                if sustained.lower() not in ('yes', 'true', 't', 'y', '1', ''):
                    rowsToDelete.append(ind)
        if len(rowsToDelete) > 0:
            self.removeCondition(rowsToDelete)
    def returnFullTable(self):
        return self.condTable
    def toText(self):
        '''
        This is what comes when you try to print the object
        '''
        if len(self.condTable) == 0:
            return ''
        fullstr = ''
        for ind in self.condTable.index:
            indexstr = f'{self.condTable.loc[ind,"Effect"]} for {self.condTable.loc[ind,"Duration"]}'
            if self.condTable.loc[ind,'Sustain']:
                indexstr += ' Sustained'
            indexstr += '; '
            fullstr += indexstr
        return fullstr
    def __repr__(self):
        return self.toText()
    def __str__(self):
        return self.toText()

if __name__ == '__main__':
    Data = pd.DataFrame(columns=['Turn', 'Name', 'Init', 'Mod', 'HP', 'Conditions'], dtype=object)
    if len(sys.argv) <= 1:
        Data = AddToInit(Data)
        print(Data)
        CurrTurn = 0
        Data['Turn'][0] = '==>'
    elif len(sys.argv) > 1:
        for arg in range(1,len(sys.argv)):
            # Load in each character one by one
            df1 = pd.read_csv(sys.argv[arg], nrows = 1, sep = ',', keep_default_na=False, dtype=str) #cast to string to make checking if Init is an integer easier
            df2 = pd.read_csv(sys.argv[arg], skiprows = 2, sep = ',')
            ind = arg - 1
            Data.loc[ind,'Name'] = df1.loc[0,'Name']
            Data.loc[ind,'Mod'] = int(df1.loc[0,'Mod'])
            Data.loc[ind,'HP'] = int(df1.loc[0,'HP'])
            print(df1.loc[0,'Init'])
            if df1.loc[0,'Init'].isnumeric():
                Data.loc[ind,'Init'] = int(df1.loc[0,'Init'])
            else:
                Data.loc[ind,'Init'] = (random.randint(1,20)+int(df1.loc[0,'Mod']))
            Data.loc[ind,'Conditions'] = ConditionManager(initialDF = df2)

        Data = Data.assign(Turn = [' ']*len(Data['Name']))
        Data = Data.reindex(columns = ['Turn', 'Name', 'Init', 'Mod', 'HP', 'Conditions'])
        #Sort the results and set initial turn
        Data = InitSort(Data)
        CurrTurn = 0
        Data.loc[0,'Turn'] = '==>'
    else:
        print('Check input filenames.')
    while True:
        #Clear window
        os.system('cls' if os.name=='nt' else 'clear')
        #Print initiatives
        print(Data.to_string())
        #Ask for actions
        Instruction = input(
'\nAvailable actions:\n \
\t[aA] Add -        Add someone to the list;\n \
\t[rR] Remove -     Remove someone from the list;\n \
\t[eE] Edit -       Change someones initiative value;\n \
\t[dD] Damage -     Apply damage/healing to someone;\n \
\t[cC] Conditions - Edit someones conditions;\n \
\t[nN] Next -       Go to next turn;\n \
\t[tT] Turn -       Forcefully set a whose turn it is;\n \
\t[sS] Save -       Save an characters to files;\n \
\t[qQ] Quit -       Exit from the tracker.\n \
Choose an action '          )
        if Instruction.lower() in ('a', 'd', 'c', 'e', 'n', 'q', 'r', 's', 't'):
            #Add to initiative
            if Instruction.lower() == 'a':
                Data = AddToInit(Data)
            #Remove from list
            elif Instruction.lower() == 'r':
                Data, CurrTurn = RemoveFromInit(Data, CurrTurn)
            #Edit Initiative from list
            elif Instruction.lower() == 'e':
                Data, CurrTurn = EditInit(Data, CurrTurn)
            #Apply damage
            elif Instruction.lower() == 'd':
                Data = ApplyDamage(Data, CurrTurn)
            #Apply Condition
            elif Instruction.lower() == 'c':
                Data = ConditionMenu(Data, CurrTurn)
            #Next turn
            elif Instruction.lower() == 'n':
                Data, CurrTurn = NextTurn(Data, CurrTurn)
            #Set a specific turn
            elif Instruction.lower() == 't':
                Data, CurrTurn = SetTurn(Data, CurrTurn)
            #Save a file
            elif Instruction.lower() == 's':
                SaveToFile(Data)
            #Quit
            elif Instruction.lower() == 'q':
                YN = input('Are you sure you want to quit? [yN] ')
                if YN.lower() in ('yes', 'true', 't', 'y', '1' ,''):
                    break
                else:
                    continue
        else:
            input('Invalid selection, retry. Hit any key to proceed. ')
            continue
