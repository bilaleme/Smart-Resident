import pandas as pd
import numpy as np
import math
from scipy import stats
stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq,df)


AirQualityCat = ['air-qual-good','air-qual-moderate','air-qual-unhealthy','air-qual-hazardous']
WeatherCat = ['weather-rainy','weather-stormy','weather-sunny','weather-cloudy','weather-hot','weather-cold','weather-dry','weather-wet','weather-windy','weather-snow']
TrafficCat = ['traffic-low','traffic-moderate','traffic-high','traffic-worse']
DayPartCat = ['dt-early-morning','dt-morning','dt-noon','dt-afternoon','dt-night','dt-late-night']
BikeLanesCat = ['bl-none','bl-partial','bl-full']
TemperatureCat = ['temp-0-10','temp-10-20','temp-20-30','temp-30-40','temp-40-50','temp-50-60','temp-60-70','temp-70-80','temp-80-90','temp-90-100']
TimeCat = ['time-1-15','time-15-30','time-30-45','time-45-60']
DistanceCat = ['dist-1-5','dist-5-10','dist-10-15','dist-15-20','dist-20-25','dist-25-30','dist-30-35']
ModesCat = ['mode-car','mode-transit','mode-bike','mode-mt-bike','mode-walk']


CatCombined = []
CatCombined.extend(AirQualityCat)
CatCombined.extend(WeatherCat)
CatCombined.extend(TrafficCat)
CatCombined.extend(DayPartCat)
CatCombined.extend(BikeLanesCat)
CatCombined.extend(TemperatureCat)
CatCombined.extend(DistanceCat)
CatCombined.extend(TimeCat)


IndCombined = []
IndCombined.extend(CatCombined)
CatCombined.extend(ModesCat)


def ConvertTemperature(intValue, tempCategories):
    myVal = math.floor(intValue / len(tempCategories) - 1)
    return tempCategories[myVal];


def ConvertAirQuality(intValue, aqCategories):
    myVal = math.ceil((intValue / 2.5) - 1)
    return aqCategories[myVal];

def ConvertDistance(intValue, dCategories):
    myVal = math.ceil((intValue / 5) - 1)
    return dCategories[myVal]

def ConvertTime(intValue, tCategories):
    myVal = math.ceil((intValue / 15) - 1)
    return tCategories[myVal]


def ComputePearson(indName, colName, dFrame):
    firstElement = dFrame.loc[indName, colName]
    secondElement = dFrame.drop(colName, axis=1).loc[indName, :].sum()
    thirdElement = dFrame.drop(indName).loc[:, colName].sum()
    fourthElement = dFrame.drop(indName).drop(colName, axis=1).sum(axis=1).sum()
    varPearson = ((firstElement * fourthElement) - (thirdElement * secondElement)) / math.sqrt(
        (firstElement + thirdElement) * (secondElement + fourthElement) * (firstElement + secondElement) * (
        thirdElement + fourthElement))
    return varPearson


def RankMode(indNames,colNames,dataFrame):
    scoreArray = [0]*len(colNames)
    for i in range(len(colNames)):
        score = 0
        for j in range(len(indNames)):
            pVal = ComputePearson(indNames[j],colNames[i],dataFrame)
            score = score + pVal * (dataFrame.loc[indNames[j],colNames[i]])
        scoreArray[i] = score
    return scoreArray

def GetObservation(obsArray, indicesArray):
    varAirQuality = ConvertAirQuality(obsArray['air-quality'],AirQualityCat)
    varWeather = indicesArray[indicesArray.index(obsArray['weather'])]
    varTraffic = indicesArray[indicesArray.index(obsArray['traffic'])]
    varDayTime = indicesArray[indicesArray.index(obsArray['day-time'])]
    varBikeLane = indicesArray[indicesArray.index(obsArray['bike-lane'])]
    varTemperature = ConvertTemperature(obsArray['temperature'],TemperatureCat)
    varDistance = ConvertDistance(obsArray['distance'],DistanceCat)
    varTime = ConvertTime(obsArray['time'],TimeCat)
    return [varAirQuality,varWeather,varTraffic,varDayTime,varBikeLane,varTemperature,varDistance,varTime]

def RecommendMode(rankMatrix, modeCats):
    return modeCats[rankMatrix.index(max(rankMatrix))]

def RecommendModeGreen(rankMatrix, modeCats):
    maxMode =  rankMatrix.index(max(rankMatrix))
    walkIndex = modeCats.index("mode-walk")
    bikeIndex = modeCats.index("mode-bike")
    walkScore = rankMatrix[walkIndex]
    bikeScore = rankMatrix[bikeIndex]
    scoreDifferenceWalk = abs(maxMode - walkScore)
    scoreDifferenceBike = abs(maxMode - bikeScore)

    maxIndex = maxMode
    maxGreenScore = 0
    if scoreDifferenceBike < scoreDifferenceWalk:
        maxIndex = bikeIndex
        maxGreenScore = scoreDifferenceBike
    elif scoreDifferenceWalk < scoreDifferenceBike:
        maxIndex = walkIndex
        maxGreenScore = scoreDifferenceWalk

    outIndex = maxMode
    if abs(rankMatrix[maxMode] - maxGreenScore) / rankMatrix[maxMode] <= 30:
        outIndex = maxIndex

    return modeCats[outIndex]






xFile = pd.ExcelFile('data.xlsx')
df = xFile.parse('data')
dataArr = np.ones((len(IndCombined), len(ModesCat)))
for i in range(len(df.index)):
    freshVal = int(df.iloc[i]['Freshness'])
    freshVal = freshVal * 10

    tAirQual = ConvertAirQuality(int(df.iloc[i]['air-quality']), AirQualityCat)
    tWeather = df.iloc[i]['weather']
    tTraffic = df.iloc[i]['traffic']
    tDayTime = df.iloc[i]['day-time']
    tDistance = df.iloc[i]['distance']
    tTime = df.iloc[i]['time']
    tBikeLanes = df.iloc[i]['bike-lane']
    tTemperature = ConvertTemperature(int(df.iloc[i]['temperature']), TemperatureCat)
    tDistance = ConvertDistance(int(df.iloc[i]['distance']), DistanceCat)
    tTime = ConvertTime(int(df.iloc[i]['time']), TimeCat)
    tMode = df.iloc[i]['mode']

    tModeIndex = ModesCat.index(tMode)
    tAirQualIndex = IndCombined.index(tAirQual)
    tWeatherIndex = IndCombined.index(tWeather)
    tTrafficIndex = IndCombined.index(tTraffic)
    tDayTimeIndex = IndCombined.index(tDayTime)
    tDistanceIndex = IndCombined.index(tDistance)
    tTimeIndex = IndCombined.index(tTime)
    tBikeLanesIndex = IndCombined.index(tBikeLanes)
    tTemperatureIndex = IndCombined.index(tTemperature)

    dataArr[tAirQualIndex][tModeIndex] = freshVal + 1
    dataArr[tWeatherIndex][tModeIndex] = freshVal + 1
    dataArr[tTrafficIndex][tModeIndex] = freshVal + 1
    dataArr[tDayTimeIndex][tModeIndex] = freshVal + 1
    dataArr[tBikeLanesIndex][tModeIndex] = freshVal + 1
    dataArr[tDistanceIndex][tModeIndex] = freshVal + 1
    dataArr[tTimeIndex][tModeIndex] = freshVal + 1
    dataArr[tTemperatureIndex][tModeIndex] = freshVal + 1

mydf = pd.DataFrame(dataArr, index=IndCombined, columns=ModesCat)

#sample code for consideration
inDict = {"air-quality":1,"weather":"weather-rainy","traffic":"traffic-high","day-time":"dt-morning","bike-lane":"bl-full","temperature":68,"distance":7,"time":16}
myObservation = GetObservation(inDict,IndCombined)
print(myObservation)
modeMat = RankMode(myObservation,mydf.columns.values,mydf)
print(RecommendMode(modeMat,ModesCat))
print(RecommendModeGreen(modeMat,ModesCat))

