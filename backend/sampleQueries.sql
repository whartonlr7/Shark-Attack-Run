/*This query replaces the getSharkSpecies function.
 The only part of the query that needs to change is the 
 condition in the where function which specifies the case_ID. */
SELECT sharkRelation.Case_ID, species.speciesName FROM species
FUll OUTER JOIN  sharkRelation ON sharkRelation.species_ID=species.species_ID
WHERE sharkRelation.Case_ID = 'ND.0110';
/* This query replaces the activityAtTimeOfSharkAttack function. 
The only part of query that changes with the parameter
of the function is the case_ID. */
SELECT sharkRelation.Case_ID, activities.activityName FROM activities
FUll OUTER JOIN  sharkRelation ON sharkRelation.activity_ID=activities.activity_ID
WHERE sharkRelation.Case_ID = 'ND.0110';

/* This query replaces the getInjury function. 
The only part of query that changes with the parameter
of the function is the case_ID. */
SELECT sharkRelation.Case_ID, injuries.injuryName FROM injuries
FUll OUTER JOIN  sharkRelation ON sharkRelation.injury_ID=injuries.injury_ID
WHERE sharkRelation.Case_ID = 'ND.0110'; 

/* This query replaces the find shark attacks in range function. 
Some of the data is incorrect and claims it is in the future we have tried our best 
to adjust the dataset but an implementaion of the function would check if the date matches
the case number or raw date to make sure it is within the date range. */
SELECT sharkRelation.Case_ID from dates
FULL JOIN sharkRelation on sharkRelation.date_ID=dates.date_ID
WHERE dates.convertedDate >= '12/12/2012'::date and dates.convertedDate <= '12/12/2018'::date;

/* This query replaces the get attack function and allows for you 
to input a case_ID and gets all the proper information by referencing
all tables. */
SELECT sharkRelation.Case_ID, dates.rawDate, countries.country,
locations.locationName, areas.areaName, injuries.injuryName, 
species.speciesName, activities.activityName FROM dates
FULL JOIN sharkRelation ON sharkRelation.Date_ID=dates.date_ID 
FULL JOIN countries on sharkRelation.country_ID=countries.Country_ID
FULL JOIN locations on sharkRelation.location_ID=locations.location_ID
FULL JOIN areas on sharkRelation.area_ID=areas.area_ID
FULL JOIN injuries on sharkRelation.injury_ID=injuries.Injury_ID
FUll JOIN species on sharkRelation.Species_ID=species.Species_ID
FULL JOIN activities on sharkRelation.activity_ID = activities.activity_ID
where sharkRelation.case_ID = 'ND.0110';

SELECT injuries.injuryName, count(sharkRelation.injury_ID) AS InjuryOccurences FROM injuries
FULL JOIN sharkrelation ON sharkRelation.injury_ID=injuries.Injury_ID
GROUP BY injuries.injuryName;

Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from countries
Full join sharkRelation on sharkRelation.country_ID = countries.country_ID
Full join areas on sharkRelation.area_ID = areas.area_ID
where countries.country = 'United States of America' group by areas.areaName
order by AreaOccurences DESC
Limit 1
;

Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas
Full join sharkRelation on sharkRelation.area_ID = areas.area_ID
where sharkRelation.country_ID = 841 group by areas.areaName
order by AreaOccurences DESC
Limit 1
;

Select Country_ID from countries where country = 'USA' or twoLetter = 'USA' or threeLetter = 'USA';

Select areaName, min(AreaOccurences) from 
(Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas
Full join sharkRelation on sharkRelation.area_ID = areas.area_ID
where sharkRelation.country_ID = 841
group by areas.areaName
order by AreaOccurences) as LeastCommonArea
group by areaName
;

Select areaName, AreaOccurences from
(Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas
Full join sharkRelation on sharkRelation.area_ID = areas.area_ID
where sharkRelation.country_ID = 841
group by areas.areaName
order by AreaOccurences) as LeastCommonArea
where AreaOccurences = (Select min(AreaOccurences) from (Select areas.areaName, count(sharkRelation.area_ID) as AreaOccurences from areas
Full join sharkRelation on sharkRelation.area_ID = areas.area_ID
where sharkRelation.country_ID = 841
group by areas.areaName
order by AreaOccurences) as LeastCommonArea)
group by areaName, AreaOccurences
;

Select locations.locationName, Areas.areaName from locations
Full Join sharkRelation on sharkRelation.location_ID = locations.location_ID
Full Join areas on sharkRelation.area_ID = areas.area_ID
Where Areas.areaName = 'Florida';