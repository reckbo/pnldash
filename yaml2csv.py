#!/usr/bin/env python
from plumbum import cli, local
import csv
import yaml
import os.path


PARAM_HDR = ['projectName', 'projectPath', 'description', 'paramId',
                   'param', 'paramValue']
PATH_HDR = ['projectName', 'projectPath', 'paramId', 'pathKey',
                    'caseid', 'path', 'exists']

def csvFromDict(d):
    s = ""
    hdr = 'projectName,projectPath,grantId,paramId,caselist,param,paramValue'
    row = ','.join(d.values())
    return hdr + '\n' + row

def readFileLines(fn):
    with open(fn, 'r') as f:
        return f.read().splitlines()

class App(cli.Application):
    def main(self, ymlfile):
        with open(ymlfile, 'r') as f:
            yml = yaml.load(f)

        name = yml['projectInfo']['projectName']
        projectInfo = yml['projectInfo']
        paramsCsv = '{}_params.csv'.format(name)
        pathsCsv = '{}_paths.csv'.format(name)

        with open(paramsCsv, 'w') as fparamsCsv:
            csvwriterParams = csv.writer(fparamsCsv)
            csvwriterParams.writerow(PARAM_HDR)
            with open(pathsCsv, 'w') as fpathsCsv:
                csvwriterPaths = csv.writer(fpathsCsv)
                csvwriterPaths.writerow(PATH_HDR)

                for paramId, pipeline in enumerate(yml['pipelines']):
                    for param, paramVal in pipeline['parameters'].items():
                        csvwriterParams.writerow([projectInfo['projectName'],
                                            projectInfo['projectPath'],
                                            projectInfo['grantId'],
                                            projectInfo['description'],
                                            paramId, param, paramVal])
                    caseids = readFileLines(pipeline['paths']['caselist'])
                    caseidString = pipeline['paths']['caseid']
                    for pathKey, pathTemplate in pipeline['paths'].items():
                        if pathKey == 'caselist' or pathKey == 'caseid':
                            continue
                        for caseid in caseids:
                            path = pathTemplate.replace(caseidString, caseid)
                            csvwriterPaths.writerow(
                                [projectInfo['projectName'],
                                 projectInfo['projectPath'],
                                 paramId,
                                 pathKey, caseid, path,
                                 os.path.exists(path)])
            print("Made '{}'".format(paramsCsv))
            print("Made '{}'".format(pathsCsv))


if __name__ == '__main__':
    App.run()
