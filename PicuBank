length = input()
for x in range(int(length)):
    tempInput = input()
    splitInput = tempInput.split()
    d = int(splitInput[0])
    a = int(splitInput[1])
    m = int(splitInput[2])
    b = int(splitInput[3])
    x = int(splitInput[4])

    x = x - d
    if (x <= 0):
        print(0)

    remainder = int(x % (a*m + b))
    output = int(x / (a*m + b))
    output = int(output * (m + 1))
    if (int(remainder % a) == 0):
        output = output + int((remainder / a))
    else:
        output = output + int((remainder / a) + 1)

    print(output)
