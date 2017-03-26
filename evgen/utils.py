from past.utils import old_div
import numpy as np
import calendar

def random_test(probability):
    """
    Probability test function. 
    """
    if np.random.random() < probability:
        return True
    else:
        return False

class Distribution(object):
    def __init__(self, elements=None, sample_size=None, weights=None):
        if elements is None and sample_size is None:
            raise ValueError('either elements or sample_size parameter is required')
        if elements is None:
            self.__elements__ = list(range(0,sample_size))
        else:
            self.__elements__ = elements
        if weights is None:

            self.__weights__ = [old_div(1.0,len(self.__elements__))]*len(self.__elements__)
        else:
            self.__weights__ = weights
        
    def get_value(self, starts=None, ends=None):
        """
        Generates random value based on provided elements and weights (probability distribution).
        Supports also subset of all elements.
        starts - beginning of subset
        ends = end of subset
        """
        if starts is None: starts== 0
        if ends is None: ends == len(self.__elements__)
        sprob = sum(self.__weights__[starts:ends])
        elements = self.__elements__[starts:ends]
        weights = [old_div(w,sprob) for w in self.__weights__[starts:ends]]
        return np.random.choice(elements, size=1, p=weights)[0]

class WeeklyDistribution(Distribution):
    def __init__(self, weights=None):
        super(WeeklyDistribution, self).__init__(elements=list(range(0,7)), weights=weights)

    def get_value(self, year, month):
        day_of_week = np.random.choice(self.__elements__, size=1, p=self.__weights__)[0]
        #turning day_of_week into absolute day number
        mcal = calendar.Calendar(0).monthdayscalendar(year, month)
        day = np.random.choice([i[day_of_week] for i in mcal if i[day_of_week] != 0], size=1)[0]
        return day

class HourlyDistribution(Distribution):
    def __init__(self, weights=None):
        super(HourlyDistribution, self).__init__(elements=list(range(0,24)), weights=weights)

class MonthlyDistribution(Distribution):
    def __init__(self, weights=None):
        super(MonthlyDistribution, self).__init__(elements=list(range(1,13)), weights=weights)            
