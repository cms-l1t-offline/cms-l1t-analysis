import urllib2
import json

def lumiFilter(run, lumi, lumiJson=''):

    # If no lumi mask json, pass all events    
    if not lumiJson:
        return True

    # Load json
    if 'https://' in lumiJson:
        response = urllib2.urlopen(lumiJson)
        lumiMask = json.load(response)
    else:
        lumiMask = json.load(open(lumiJson))

    if str(run) in lumiMask:
        for ls_list in lumiMask[str(run)]:
            if lumi >= ls_list[0] and lumi <= ls_list[1]:
                return True

    return False
