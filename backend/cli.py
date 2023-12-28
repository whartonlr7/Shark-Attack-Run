from api import *

import os

def clear():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

def main():
    print('Welcome to Shark Attack Run Terminal Client!!! \nPress enter to continue')
    input()
    clear()
    dataset = Dataset()
    number = 0
    while not number == 11:
        print("What Function Would you like to try?\n------------")
        print('1. Find the most common area for sharks in a country')
        print('2. Find the safest beach from coordinates')
        print('3. Find the safest beach in a country')
        print('4. Find the most common body parts injured in shark attacks')
        print('5. Find the most common species involved in shark attacks')
        print('6. Compare the details of two shark attack incidents')
        print('7. For a given shark attack gets the species of shark')
        print('8. Find the activity a person was engaged in for a given shark attack')
        print('9. Shark attacks in a date range')
        print('10. Quit the program')
        print('------------')
        number = input("Enter the number of what you want to do: ")
        
        while type(number) == str:
            try:
                number = int(number)
            except ValueError:
                number = input('Please put a valid integer: ')
        
        match number:
            case 1:
                country = input('Enter a Country: ')
                validCountry = False
                coordinates = None
                while not validCountry:
                    try:
                        coordinates = dataset.mostCommonSharkArea(country)
                        validCountry = True
                    except Exception:
                        print('Not a valid Country')
                        validCountry = False
                        country = input('Enter a Country: ')
                print("The most common shark attack location in", country, "is at the coordinates", coordinates)
                input("Press Enter to continue")
                clear()
            case 2:
                Latitude = input("Enter the latitude for where you want to search: ")
                Longitude = input("Enter the longitude for where you want to search: ")

                while not type(Latitude) == float and not type(Longitude) == float:
                    try:
                        Latitude = float(Latitude)
                    except ValueError:
                        Latitude = input("Enter A valid latitude for where you want to search: ")
                    try:
                        Longitude = float(Longitude)
                    except ValueError:
                        Longitude = input("Enter A valid Longitude for where you want to search: ")

                if input("Would you like to use optional parameters Y/N: ").capitalize() == 'Y':
                    optionalAreaSize = input("Enter search area size (km): ")
                    try:
                        optionalAreaSize = int(optionalAreaSize)
                    except ValueError:
                        optionalAreaSize = input('Please put a valid integer: ')
                else:
                    optionalAreaSize = 10000

                coordinates = (Latitude, Longitude)
                SafeBeachCoordinates = dataset.safestBeachFromCoordinates(coordinates)
                print('The safest beachs are:')
                for beaches in SafeBeachCoordinates:
                    print(beaches)
                input('Press enter to continue')
                clear()
            case 3: 
                country = input('Enter a Country: ')
                validCountry = False
                coordinates = []
                while not validCountry:
                    try:
                        coordinates = dataset.safestBeachFromCountry(country)
                        validCountry = True
                    except Exception:
                        print('Not a valid Country')
                        validCountry = False
                        country = input('Enter a Country: ')
                
                print('The safest beaches are:')
                for Beaches in coordinates:
                    print(Beaches)
                input('Press enter to continue')
                clear()
            case 4:
                body_parts = dataset.getBodyParts()
                for key, value in body_parts.items():
                    print(f'Sharks have attacked the {key} {value} times')
                input('Press enter to continue')
                clear()
            case 5:
                species = dataset.getSpecies()
                print('The shark species breakdown is as follows:')
                for key, value in species.items():
                    print(f'{key}s have attacked humans {value} times')
                input('Press enter to continue')
                clear()
            case 6:
                attack1 = input('Enter the ID of one shark attack: ')
                attack2 = input('Enter the ID of another shark attack to compare: ')
                comparison = dataset.compareAttacks(attack1, attack2)
                if not comparison == None:
                    for factor in comparison:
                        print(factor)
                else:
                    print('Not Valid Id')
                input('Press enter to continue')
                clear()
            case 7:
                attack = input('Enter the ID of a shark attack: ')
                species = dataset.getSharkSpecies(attack)
                print('The shark involved in shark attack', attack, 'was a', species)
                input('Press enter to continue')
                clear()
            case 8:
                attack = input('Enter the ID of a shark attack: ')
                activity = dataset.activityAtTimeOfSharkAttack(attack)
                print('At the time of shark attack', attack, 'the victim was', activity.lower())
                input('Press enter to continue')
                clear()
            case 9:
                while True:
                    date1 = input('Enter the beginning date for your date range (mm/dd/yyyy): ')
                    date2 = input('Enter the ending date for your date range (mm/dd/yyyy): ')
                    try:
                        date1 = (int(date1[0:2]), int(date1[3:5]), int(date1[6:]))
                        date2 = (int(date2[0:2]), int(date2[3:5]), int(date2[6:]))
                    except Exception:
                        print('Please input your data in the mm/dd/yyyy format')
                        continue
                    attacksInRange = dataset.sharkAttacksInDateRange(date1, date2)
                    if attacksInRange == None:
                        print('At least one of your days was either not real or in the future')
                        continue
                    break
                print('There were', len(attacksInRange), 'shark attacks between', date1, 'and', date2)
                print(*attacksInRange, sep= "\n")
                input('Press enter to continue')
                clear()
            case 10:
                print('Good bye! I hope you learned more about sharks!!')
            case _:
                print("Not a valid function")
                input("Press enter to continue")
                clear()
                
if __name__ == '__main__':
    main()
