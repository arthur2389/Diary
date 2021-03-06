import abc
from os import path

from EnumAndConsts.EnumsAndConsts import ECompletionStatus as CompStatus
from KortexCore.CommonUtils.DataModerator import DataModerator
from KortexCore.File.FunctionalFile import FunctionalFile
from KortexCore.CommonUtils.JsonIO import JsonIO


class PropertyBase(object):
    """
    Abstract base class for event property. A property is a characterization unit of the event.
    """

    def __init__(self, dir_path):
        """
        param: dirPath: each property is initiated by it's metadata directory path (str)
        """
        self._data_moderator = DataModerator()
        self._path = path.join(dir_path, self._data_moderator.get_data(group="project_consts",
                                                                       parameter="project_repo_name"))

    @abc.abstractmethod
    def load_existing(self):
        """
        Load existing property from metadata file.
        """
        pass

    @abc.abstractmethod
    def assign(self, assign_args, **kwargs):
        """
        Assign new value to the property
        """
        pass

    @abc.abstractmethod
    def get(self):
        """
        Get the value of a property
        """
        pass

    def __str__(self):
        """
        Debug method for representing a property
        """
        return str(self.get())


class Image(PropertyBase):

    suffixes = [".jpg", ".png", ".gif", ".svg"]

    def __init__(self, dir_path):
        super(Image, self).__init__(dir_path)
        img_name = self._data_moderator.get_data(group="project_consts", parameter="default_event_image")
        img_path = self._data_moderator.get_file_path(group="user_project", name=img_name)
        self._img = FunctionalFile(name=path.basename(img_path),
                                   dir_name=path.dirname(img_name))

    def load_existing(self):
        """
        Load existing property by searching for the specified file
        """
        for suffix in self.__class__.suffixes:
            if path.exists(path.join(self._path, self.__class__.__name__ + suffix)):
                self._img = FunctionalFile(name=self.__class__.__name__ + suffix,
                                           dir_name=self._path,
                                           level=0,
                                           holding_dir=None)
                break

    def assign(self, assign_args, **kwargs):
        """
        param: filePath: assign new file to property by copying and replacing the old file
        """
        self._img = FunctionalFile(name=path.basename(assign_args.img_path),
                                   dir_name=path.dirname(assign_args.img_path))
        if self._img.suffix not in self.__class__.suffixes:
            raise FileNotFoundError
        self._img.copy(target_dir_path=self._path, new_name=self.__class__.__name__)

    def get(self):
        """
        Returns the full path of the file
        return: file full path (str) or None the is no file
        """
        return self._img.path


class DescriptionProperty(PropertyBase):

    """
    Description property stand for a property that can be described by text. The data of the property
    will be held in event's metadata file, that is placed in events metadata folder.
    """
    def __init__(self, dir_path):
        super(DescriptionProperty, self).__init__(dir_path)
        self._data_file_path = path.join(self._path, self._data_moderator.get_data(group="project_consts",
                                                                                   parameter="event_data_file_name"))
        self._desc = None

    def load_existing(self):
        """
        Load existing property from metadata file
        """
        data = JsonIO.read(self._data_file_path)
        if self.__class__.__name__ in data:
            self._set_desc(data[self.__class__.__name__])

    def assign(self, assign_args, **kwargs):
        """
        Write a new description to metadata file
        param: desc: description to write (str)
        """
        JsonIO.write(self._data_file_path, self.__class__.__name__, assign_args)

    def get(self):
        """
        return: event's description (str)
        """
        return self._desc

    @abc.abstractmethod
    def _set_desc(self, desc_str):
        """
        Abstract method that is called when loading a description
        param: descStr: description from metadata file
        """
        pass


class CompletionStatus(DescriptionProperty):

    def __init__(self, dir_path):
        super(CompletionStatus, self).__init__(dir_path)
        self._desc = CompStatus.NOT_COMPLETED

    def assign(self, assign_args, **kwargs):
        """
        Assign new description
        param: propArgs: argument object that holds description field (KortexKoreInterface.PropertyArgs)
        """
        self._desc = assign_args.completion_status
        super(CompletionStatus, self).assign(assign_args=assign_args.completion_status.name)

    def _set_desc(self, desc_str):
        """
        Assign loaded description
        param: descStr: loaded description (str)
        """
        self._desc = getattr(CompStatus, desc_str)


class Description(DescriptionProperty):

    """
    Event description string. Free description section about the event
    """
    def __init__(self, dir_path, name):
        super(Description, self).__init__(dir_path)
        self._desc = "Event: " + name

    def assign(self, assign_args, **kwargs):
        """
        Assign new description
        param: propArgs: argument object that holds description field (KortexKoreInterface.PropertyArgs)
        """
        self._desc = assign_args.description
        super(Description, self).assign(assign_args=assign_args.description)

    def get(self):
        """
        return: event's description (str)
        """
        return self._desc

    def _set_desc(self, desc_str):
        """
        Assign loaded description
        param: descStr: loaded description (str)
        """
        self._desc = desc_str


class QuantifiableProperty(DescriptionProperty):

    """
    Base class of a description that can is countable and comparable.
    """
    @abc.abstractmethod
    def __int__(self):
        """
        QuantifiableProperty object must have an explicit ability to be casted to integer
        """
        pass


class Importance(QuantifiableProperty):

    """
    Event importance. Represented by KortexEnums.Importance enumeration
    """
    def __init__(self, dir_path):
        """
        Default importance is set to trivial
        """
        super(Importance, self).__init__(dir_path)
        self._metrics = self._data_moderator.get_data(group="event_properties",
                                                      parameter="importance_metrics")
        self._importance = "trivial"

    def assign(self, assign_args, **kwargs):
        """
        Assign new importance value
        param: propArgs: argument object that holds importance field (KortexKoreInterface.PropertyArgs)
        """
        self._importance = assign_args.importance
        super(Importance, self).assign(assign_args=assign_args.importance)

    def get(self):
        """
        return: event importance (KortexEnums.Importance)
        """
        return self._importance

    def __int__(self):
        """
        Cast to integer by taking the value of the enumeration
        return: importance value (int)
        """
        return self._metrics[self._importance]

    def _set_desc(self, desc_str):
        """
        """
        self._importance = desc_str


class CashFlow(QuantifiableProperty):
    """
    Represents money input or output of the event
    """

    def __init__(self, dir_path):
        super(CashFlow, self).__init__(dir_path)
        self._cash_flow = 0

    def assign(self, assign_args, **kwargs):
        """
        Assign new money balance value
        param: propArgs: argument object that holds moneyBalance field (KortexKoreInterface.PropertyArgs)
        """
        self._cash_flow = assign_args.cash_flow
        super(CashFlow, self).assign(assign_args=assign_args.cash_flow)

    def get(self):
        """
        """
        return self._cash_flow

    def __int__(self):
        """
        return: money balance value (int)
        """
        return int(self._cash_flow)

    def _set_desc(self, desc_str):
        """
        Convent string money balance to integer field
        param: descStr: money balance (str)
        """
        self._cash_flow = int(desc_str)


class DateAndTime(QuantifiableProperty):

    def __init__(self, dir_path, handler):
        """
        Initialize date and time by default values
        """
        super(DateAndTime, self).__init__(dir_path)
        self._date_and_time = None
        self._handler = handler

    def assign(self, date_and_time, **kwargs):
        """
        """
        self._date_and_time = date_and_time
        super(DateAndTime, self).assign(assign_args=self.__str__())

    def get(self):
        """
        """
        return self._date_and_time

    def __str__(self):
        return self._date_and_time.ctime()

    def __int__(self):
        """
        Cast data and time to integer by summing the total number of minutes
        return: total number of minutes (int)
        """
        return int(self._handler.time_length(self._date_and_time))

    def _set_desc(self, desc_str):
        """
        Parse date and time input from metadata file and assign in object
        param descStr: data and time from file (str)
        """
        self._date_and_time = self._handler.date_time_from_ctime(desc_str)


class StartDateAndTime(DateAndTime):
    pass


class EndDateAndTime(DateAndTime):
    pass
