
import matplotlib.pyplot as plt
import covid19poland as PL

# logging
import logging
logging.basicConfig(level = logging.INFO)

# fetch
x = PL.covid_tests(offline = True)
print(x)

plt.plot(x.date, x.tests)
plt.show()
#print(x)
# save to file
#x.to_csv("covid_tests_poland.csv", index = False)

