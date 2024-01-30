while True:
    ans = input(
        'What would you like to do today?\n [0] Add a filter | [1] Remove a filter | [2] Run a filter | [3] Run all filters | [4] Change configurations | [5] Exit\n Enter a number 0-5:')
    try:
        ans = int(ans)
    except:
        ValueError
        print("Please enter a number 0-5")
        continue

    if ans not in range(0, 6):
        print("Please enter a number 0-5")
    elif ans == 5:
        print('Bye!')
        break