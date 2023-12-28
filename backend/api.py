from datetime import datetime
from functools import partial
import os
import csv
import reverse_geocoder
import psycopg2
import psqlConfig as config
import random
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as mpl


class Dataset:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(database=config.database, user=config.user, password=config.password, host=config.host)
        except Exception as e:
            print("Connection error: ", e)
            exit()
        self.cur = self.connection.cursor()

    def checkValidCountry(self, country: str):
        if isinstance(country, int):
            return country
        self.cur.execute('Select Country_ID from countries where country = %s or twoLetter = %s or threeLetter = %s;',(country, country, country))
        result = self.cur.fetchone()
        if result == None:
            raise Exception('Not a valid Country 1')
        return result[0]

    def getAttacksByCountry(self, country):
        CountryID = self.checkValidCountry(country)
        self.cur.execute("SELECT sharkRelation.Case_ID, dates.rawDate, countries.country, locations.locationName, areas.areaName, injuries.injuryName, species.speciesName, activities.activityName FROM dates FULL JOIN sharkRelation ON sharkRelation.Date_ID=dates.date_ID FULL JOIN countries on sharkRelation.country_ID=countries.Country_ID FULL JOIN locations on sharkRelation.location_ID=locations.location_ID FULL JOIN areas on sharkRelation.area_ID=areas.area_ID FULL JOIN injuries on sharkRelation.injury_ID=injuries.Injury_ID FUll JOIN species on sharkRelation.Species_ID=species.Species_ID FULL JOIN activities on sharkRelation.activity_ID = activities.activity_ID where countries.country = %s;", (CountryID,))
        list_of_attacks = self.cur.fetchall()
        return list_of_attacks
            
    def sharkAttackOfDay(self):
        currentDate = datetime.now()
        intDate = ((currentDate.year*10000) + (currentDate.month * 100) + (currentDate.day))/100000000
        self.cur.execute("SELECT setseed(%s);", (intDate,))
        self.cur.execute("SELECT Case_ID from sharkrelation ORDER BY Random() LIMIT 1;")
        attack = self.cur.fetchone()
        return attack
    
    def getAllCountries(self):
        self.cur.execute("Select country_id, country from countries Order by country ASC;")
        countries = self.cur.fetchall()
        return countries
    
    def getCountryById(self, id):
        self.cur.execute("Select country from countries where country_id = %s", (id,))
        return self.cur.fetchone()[0]
        
    
    def sharkAttacksInDateRange (self, dateOne, dateTwo):
        '''A function used to find shark attacks taking place globally between dateOne
        and dateTwo
        
        Takes in two seperate dates as parameters. The dataset will be imbedded into
        the function. Returns a list of shark attack entries between dateOne and dateTwo
        Raises an error if dateTwo comes before dateOne or if either date is in the 
        future'''
        
        self.cur.execute("SELECT sharkRelation.Case_ID from dates FULL JOIN sharkRelation on sharkRelation.date_ID=dates.date_ID WHERE dates.convertedDate >= %s::date and dates.convertedDate <= %s::date ORDER BY sharkRelation.Case_ID ASC;", (f'{dateOne[1]}/{dateOne[2]}/{dateOne[0]}', f'{dateTwo[1]}/{dateTwo[2]}/{dateTwo[0]}'));
        list_of_attacks = self.cur.fetchall()
        i=0
        while i < len(list_of_attacks):
            try:
                if not (dateOne[0] <= int(list_of_attacks[i][0][0:4]) <= dateTwo[0]):
                    list_of_attacks.pop(i)
                    continue
                else:
                    i+=1
            except Exception:
                list_of_attacks.pop(i)
        return list_of_attacks

        
    def getBodyParts(self, entries):
        '''Function which returns a dictionary containing most common body parts injured in
        shark attacks
        
        Has a dictionary with body parts for example: head, arm, foot, hand, leg. Each entry
        that has one of those in it increments the count on that body part. The dictionary
        is returned to allow for the creation of a bar graph.
        '''
        # all body parts that appear in at least 20 injuries
        count = {'leg' : 0, 'foot' : 0, 'hand' : 0, 'thigh' : 0, 'arm' : 0, 'calf' : 0, 'ankle' : 0, 'forearm' : 0, 'knee' : 0, 'shoulder' : 0, 'torso' : 0, 'wrist' : 0, 'heel' : 0, 'back' : 0, 'chest' : 0, 'abdomen' : 0, 'buttock' : 0, 'finger' : 0, 'hip' : 0, 'elbow' : 0, 'toe' : 0, 'leg' : 0, 'shin' : 0, 'other' : 0}
        for entry in entries:
            if entry[5] is not None:
                words = entry[5].split(' ')
                self.incrementCountForFoundWords(count, words)
        return count
    
    def getSpecies(self, entries) -> dict:
        '''Function which returns a dictionary containing the shark breeds given by dataset
        
        Creates dictionary key for each value in dataset as well as the number of appearances.
        For example tiger shark maps to a value. This can allow the creation of a bar graph by
        looping over the dictionary.
        '''
        # all shark breeds that have been responsible for at least 20 attacks
        count = {'white' : 0, 'tiger' : 0, 'bull' : 0, 'blacktip' : 0, 'nurse' : 0, 'whaler' : 0, 'bronze' : 0, 'reef' : 0, 'grey' : 0, 'spinner' : 0, 'mako' : 0, 'wobbegong' : 0, 'blue' : 0, 'hammerhead' : 0, 'raggedtooth' : 0, 'whitetip' : 0, 'sandtiger' : 0, 'zambesi' : 0, 'other' : 0}
        for entry in entries:
            if entry[6] is not None:
                words = entry[6].split(' ')
                self.incrementCountForFoundWords(count, words)
        return count
    
    def incrementCountForFoundWords(self, count:dict, words:list):
        in_other = True
        for word in words:
            word = word.lower()
            if word in count.keys():
                count[word] += 1
                in_other = False
            # account for plurals or entries that ended with commas.
            if word[:-1] in count.keys():
                count[word[:-1]] += 1
                in_other = False
        if in_other:
            count['other'] += 1
        
    def getAttackByID(self, id):
        self.cur.execute("SELECT sharkRelation.Case_ID, dates.rawDate, countries.country, locations.locationName, areas.areaName, injuries.injuryName, species.speciesName, activities.activityName FROM dates FULL JOIN sharkRelation ON sharkRelation.Date_ID=dates.date_ID FULL JOIN countries on sharkRelation.country_ID=countries.Country_ID FULL JOIN locations on sharkRelation.location_ID=locations.location_ID FULL JOIN areas on sharkRelation.area_ID=areas.area_ID FULL JOIN injuries on sharkRelation.injury_ID=injuries.Injury_ID FUll JOIN species on sharkRelation.Species_ID=species.Species_ID FULL JOIN activities on sharkRelation.activity_ID = activities.activity_ID where sharkRelation.case_ID = %s;", (id,))
        return self.cur.fetchone()

    def getAttacksByID(self, attack_ids):
        attacks = []
        if attacks is not None:
            for attack_id in attack_ids:
                attacks.append(self.getAttackByID(attack_id))
        return attacks

    def getAllIDs(self):
        self.cur.execute('SELECT Case_ID FROM sharkRelation ORDER BY Case_ID ASC')
        return self.cur.fetchall()
    
    def compareAttacks(self, attack1, attack2):

        '''Function which compares details of two attacks
        
        Returns a list with the comparisons inside formatted as attack1 vs attack2 to allow
        for easy comparison on the user's end.
        '''
        attackEntry1 = self.getAttackByID(attack1)
        attackEntry2 = self.getAttackByID(attack2)
        if attackEntry1 == None or attackEntry2 == None:
            return None
        
        #Uses other created functions to get the neccesary information
        comparison = []
        date1 = attackEntry1[1] if attackEntry1[1] != None else 'Unknown'
        date2 = attackEntry2[1] if attackEntry2[1] != None else 'Unknown'
        country1 = attackEntry1[2] if attackEntry1[2] != None else 'Unknown'
        country2 = attackEntry2[2] if attackEntry2[2] != None else 'Unknown'
        species1 = attackEntry1[6] if attackEntry1[6] != None else 'Unknown'
        species2 = attackEntry2[6] if attackEntry2[6] != None else 'Unknown'
        activity1 = attackEntry1[7] if attackEntry2[7] != None else 'Undisclosed'   
        activity2 = attackEntry2[7] if attackEntry2[7] != None else 'Undisclosed'
        injury1 = attackEntry1[5] if attackEntry1[5] != None else 'Undisclosed'
        injury2 = attackEntry2[5] if attackEntry2[5] != None else 'Undisclosed'

        #adds each comparison to an array
        comparison.append("Attack ID: " + attack1 + " vs " + attack2)
        comparison.append("Date: " + date1 + " vs " + date2)
        comparison.append("Country: " + country1 + " vs " + country2)
        comparison.append("Species: " + species1 + " vs " + species2)
        comparison.append("Activity: " + activity1 + " vs " + activity2)
        comparison.append("Injury: " + injury1 + " vs " + injury2)
        return comparison  

    def getInjury(self, sharkAttackID):
        '''A function used to find the injury of a person involved in a given shark attack
        
        Takes in a specific shark attack as a parameter and returns the injury.'''
        correspondingSharkAttack = self.getAttackByID(sharkAttackID)
        if correspondingSharkAttack == 0 or correspondingSharkAttack == None:
            return None
        if correspondingSharkAttack[5] == None:
            return "Undisclosed"
        else:
            return correspondingSharkAttack[5]

    def getSharkSpecies(self, sharkAttackID):
        '''A function used to find the species of shark involved in a given shark attack
        
        Takes in a specific shark attack as a parameter and returns the shark species.'''
        correspondingShark = self.getAttackByID(sharkAttackID)
        if correspondingShark == 0 or correspondingShark == None:
            return None
        elif correspondingShark[6] == None:
            return "Unknown"
        else:
            return correspondingShark[6]


    def activityAtTimeOfSharkAttack (self, sharkAttackID):
        '''A function used to find the activity that a shark attack victum was engaged
        in at the time of the incident
        Takes in a specific shark attack as a parameter and returns the activity of the
        victum.'''

        correspondingSharkAttack = self.getAttackByID(sharkAttackID)
        if correspondingSharkAttack == None or correspondingSharkAttack == 0:
            return None
        elif correspondingSharkAttack[7] == None:
            return "Undisclosed"
        else:
            return correspondingSharkAttack[7]

    def mostCommonSharkArea(self, country: str):
        '''A Function used to find the most common area to find sharks in a given country.
        
        Given a country the function calculates the most common
        location where shark attacks have happened in the past which indicates shark activity. 
        The function takes a country as a parameter then a string containing
        the location. Throws an exception if provided string is not a country.
        '''
        CountryID = self.checkValidCountry(country)
        self.cur.execute('Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas Full join sharkRelation on sharkRelation.area_ID = areas.area_ID where sharkRelation.country_ID = %s group by areas.areaName order by AreaOccurences DESC Limit 4;', (CountryID,))
        safeArea = self.cur.fetchall()
        if safeArea is not None:
            for area in safeArea:
                if area[0] is not None:
                    safeArea = area[0]
                    break
        return safeArea

    def leastCommonSharkArea(self, country: str) -> list:
        '''A Function used to find the most common area to find sharks in a given country.
        
        The function calculates the most common location where shark attacks have 
        happened in the past which indicates shark activity. 
        The function takes a country as a parameter then a string containing
        the location. Throws an exception if provided string is not a country.
        '''
        CountryID = self.checkValidCountry(country)
        leastCommonAreaList = []
        self.cur.execute('Select areaName, AreaOccurences from (Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas Full join sharkRelation on sharkRelation.area_ID = areas.area_ID where sharkRelation.country_ID = %s group by areas.areaName order by AreaOccurences) as LeastCommonArea where AreaOccurences = (Select min(AreaOccurences) from (Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas Full join sharkRelation on sharkRelation.area_ID = areas.area_ID where sharkRelation.country_ID = %s group by areas.areaName order by AreaOccurences) as LeastCommonArea) group by areaName, AreaOccurences;', (CountryID, CountryID,))
        for area in self.cur:
            leastCommonAreaList.append(area[0])
        return leastCommonAreaList

    def safestBeachFromCoordinates(self, coordinates: tuple) -> list:
        '''A function used to calculate the safest beach in a given area
        
        Using staring coordinates for the center of the search range, the function will calculate the safest beach in the area
        by calculating the least common locations that shark attacks have occured. Optional parameter to adjust search distance in kilometers.
        The function returns a list containing the safest beaches in the area
        '''
        countryCode = self.whatCountry(coordinates)
        safeLocation = self.safestBeachFromCountry(countryCode)
        
        return safeLocation

    def whatCountry(self, coordinates):
        '''A function that calculates using the GeoPy module the country that contains the given coordinates'''

        location = reverse_geocoder.search(coordinates)
        countryAbreviation = location[0]['cc']
        countryCode = self.checkValidCountry(countryAbreviation)
        return countryCode


    def safestBeachFromCountry(self, country) -> list:
        '''A function to calculate the safest beach from a given country
        
        Using a starting country the function will find the safest beach on its shore that has had the least amount of shark attacks.'''

        leastCommonArea = self.leastCommonSharkArea(country)
        sharkAttackInArea = []
        safeLocations = []
        for Area in leastCommonArea:
            self.cur.execute('Select locations.locationName, Areas.areaName from locations Full Join sharkRelation on sharkRelation.location_ID = locations.location_ID Full Join areas on sharkRelation.area_ID = areas.area_ID Where Areas.areaName = %s;', (Area,))
            for Location in self.cur:
                sharkAttackInArea.append(Location)
        for Location in sharkAttackInArea:
            if Location[0] == '' or Location[0] == None or Location[1] == None:
                continue
            else:
                safeLocations.append(Location[0] + ', ' + Location[1])
        return safeLocations

    def createheatmap(self, CaseIDs, fileName: str = None):
        coordinateList = []
        for CaseId in CaseIDs:
            self.cur.execute("Select Latitude, Longitude from coordinates where Case_ID = %s", (CaseId,))
            coordinates = self.cur.fetchone()
            if coordinates is None or coordinates[0] is None or coordinates[1] is None:
                continue
            coordinateList.append(coordinates)
        map_obj = folium.Map(zoom_start=5)
        HeatMap(coordinateList).add_to(map_obj)
        if fileName is not None:
            map_obj.save(fileName)
        return map_obj

    def getAllIdsByCountry(self, CountryID:int) -> list:
        self.cur.execute('Select Case_Id from sharkRelation where country_ID = %s order by Case_Id ASC', (CountryID,))
        return self.cur.fetchall()

    def getAllIdsByActivity(self, ActivityID:int) -> list:
        self.cur.execute('Select Case_Id from sharkRelation where Activity_ID = %s order by Case_Id ASC', (ActivityID,))
        return self.cur.fetchall()

    def getAllIdsBySpecies(self, SpeciesId:int) -> list:
        self.cur.execute('Select Case_Id from sharkRelation where species_ID = %s order by Case_Id ASC', (SpeciesId,))
        return self.cur.fetchall()

    def getAllSpecies(self):
        self.cur.execute("Select species_ID, speciesName from species Order by speciesName ASC;")
        species = self.cur.fetchall()
        return species

    def getAllActivities(self):
        self.cur.execute("Select activity_id, activityName from activities Order by activityName ASC;")
        activities = self.cur.fetchall()
        return activities


def mergeIDs(list1, list2):
    """
    Returns list of common entries between two lists. It is assumed that the lists are sorted prior to entering this
    function
    """
    mutualIDs = []
    i = 0
    j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            i += 1
        elif list1[i] > list2[j]:
            j += 1
        else:
            mutualIDs.append(list1[i])
            i += 1
            j += 1
    return mutualIDs


def sharkAttackulator(results):
    ratio = 0.1
    if results['name'].lower() == 'bryce':
        ratio = 1
    if results['name'].lower() == 'will':
        ratio = -12
    if results['storm'] == 'yes':
        ratio += 0.2
    if results['storm'] == 'no':
        ratio -= 0.1
    else:
        ratio += 0.3
    if results['breakfast'] == 'eggs' or results['breakfast'] == 'pancakes':
        ratio -= 0.23
    if results['breakfast'] == 'milk' or results['breakfast'] == 'cookies':
        ratio += 0.03
    else:
        ratio += 0.23
    if results['touch'] == 'yes':
        ratio += 0.16
    else:
        ratio -= 0.2
    if results['number'] == 'noAnswer':
        ratio += 0.21
    else:
        ratio -= 0.01
    if results['limbs'] == 'yes':
        ratio += 0.2
    else:
        ratio -= 0.1
    if results['behind'] == 'yes':
        ratio += 0.64
    else:
        ratio -= 0.1
    if results['soup'] == 'yes':
        ratio += 0.14
    else:
        ratio -= 0.01

    if ratio > 1:
        ratio = 1
    elif ratio < 0:
        ratio = 0

    ratio = int(ratio*100)
    falseCount = 100 - ratio
    randomList = []
    for i in range(ratio):
        randomList.append("RUN....QUICK!")
    for i in range(falseCount):
        randomList.append("YOU ARE SAFE...FOR NOW")
    
    sharkAttackHappening = random.choice(randomList)
    
    return [sharkAttackHappening, ratio]


def makeBarChart(data, file_destination):
    names = list(data.keys())
    values = list(data.values())
    mpl.rcParams.update({'font.size': 16})
    mpl.figure(figsize=(len(names) + 10, 9/16 * (len(names) + 10)))
    mpl.bar(range(len(data)), values, tick_label=names, width=1)
    mpl.savefig(file_destination)

