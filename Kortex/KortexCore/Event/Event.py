from Kortex.KortexData.KortexEnums import EPropertyType as EPropertyType
import Kortex.KortexCore.Event.EventProperties as EventProperties


class Event(object):

    def __init__(self, directory):
        self._dir = directory
        self._propObjs = {EPropertyType.DESCRIPTION: EventProperties.Description(self._dir.path),
                          EPropertyType.IMAGE: EventProperties.Image(self._dir.path),
                          EPropertyType.IMPORTANCE: EventProperties.Importance(self._dir.path),
                          EPropertyType.DATE_AND_TIME: EventProperties.DateAndTime(self._dir.path)}

    def LoadProperties(self):
        for prop in self._propObjs.values():
            prop.LoadExisting()

    def SetDirectory(self, directory):
        self._dir = directory

    def GetDirectory(self):
        return self._dir

    def GetProperty(self, propName):
        return self._propObjs[propName]

    def __setitem__(self, propName, prop):
        self._propObjs[propName] = prop

    def __getitem__(self, propName):
        return self._propObjs[propName].Get()
