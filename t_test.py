  # read in data from files for simulation and simulation_closure
  directory = os.getcwd()

  # initialise arrays
  init_data = np.zeros(12)
  closure_data = np.zeros(12)

  # for each region in simulation
  for i in range(1, 7):
      # navigate to weekday folder
      filename = directory + os.sep + "simulation" + os.sep + \
          "weekday_results" + os.sep + \
          "Simulation Results for Region " + str(i)
      # read in average value from first line of file
      weekday_data = np.genfromtxt(
          filename, delimiter=":", skip_footer=3)
      # do the same for weekend results
      filename = directory + os.sep + "simulation" + os.sep + \
          "weekend_results" + os.sep + \
          "Simulation Results for Region " + str(i)
      weekend_data = np.genfromtxt(filename, delimiter=":", skip_footer=3)

      # append data to arrays
      init_data[i-1] = weekday_data[1]
      init_data[i+5] = weekend_data[1]

  # for each region in the simulation with closures do same as previous
  for i in range(1, 7):
      filename = directory + os.sep + "simulation_closure" + os.sep + \
          "weekday_results" + os.sep + \
          "Simulation with Closed Stores Results for Region " + str(i)
      if i == 6:
          # skip header for file which notes DailyFreight use
          weekday_data = np.genfromtxt(
              filename, delimiter=":", skip_header=1, skip_footer=3)
      else:
          weekday_data = np.genfromtxt(
              filename, delimiter=":", skip_footer=3)

      filename = directory + os.sep + "simulation_closure" + os.sep + \
          "weekend_results" + os.sep + \
          "Simulation with Closed Stores Results for Region " + str(i)
      weekend_data = np.genfromtxt(
          filename, delimiter=":", skip_footer=3)

      closure_data[i-1] = weekday_data[1]
      closure_data[i+5] = weekend_data[1]

  # prepare data for stats analysis
  sms.DescrStatsW(init_data).tconfint_mean(alpha=0.05)

  # perform mean comparison on initial simulation vs. sim with closure
  TwoSamp = sms.CompareMeans(sms.DescrStatsW(
      init_data), sms.DescrStatsW(closure_data))

  # print results
  print(TwoSamp.ttest_ind())
  print(TwoSamp.tconfint_diff())
