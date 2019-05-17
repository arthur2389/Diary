from shutil import move
from os import path, remove

from Kortex.KortexCore.File.File import File as File


class FuncrionalFile(File):

    def __init__(self, name, dirname, level, holdingDir):
        super(FuncrionalFile, self).__init__(name=name, dirname=dirname, level=level, holdingDir=holdingDir)
        self._suffix = "." + name.split(".")[-1]

    @property
    def suffix(self):
        return self._suffix

    def CopyFile(self, dest, newName=None):
        super(FuncrionalFile, self).CopyFile(dest=dest)
        if not newName:
            return
        assert isinstance(newName, str)
        newName = newName + self._suffix

        move(path.join(dest, self._name), path.join(dest, newName))

        self._dirname = dest
        self._name = newName

    def Remove(self):
        if self._holdingDir:
            self._holdingDir.RemoveFunctionalFile(self)
        remove(self.path)
        del self

    def Move(self, targetDir):
        if self._holdingDir:
            self._holdingDir.RemoveFunctionalFile(self)
        move(self.path, path.join(targetDir.path, self.name))
        targetDir.AddFunctionalFile(self)
        self._holdingDir = targetDir

    def __str__(self):
        super(FuncrionalFile, self).__str__()
        return self._tabs + self._name + "\n"

