from datetime import datetime

ten_power = 6
file_name = 'test_log_file_'+str(10**ten_power)+'_recs.log'

sample_no = {
    0: "Zero",
    1: "One",
    2: "Two",
    3: "Three"
}

sample_text = {
    0: " - America - 1 million records need to be created. I hope it crosses 1 GB size",
    1: " - Bahamas - Looping through these values to generate extensive data",
    2: " - Canada  - Made a new log entry to generate large amounts of data",
    3: " - Denmark - This is for creating a big file with too much text",
    4: " - Ethopia - Sample long text here for creating a huge file"
}

f = open(file_name, "a")
for i in range(0,(10**ten_power)):
    left_zeros = "0"*(ten_power-len(str(i)))
    timestamp = str(datetime.now())
    time = timestamp + '-' + left_zeros+str(i)

    rem_no = (i % len(sample_no))
    rem_text = (i % len(sample_text))

    f.write(time + ' ' + sample_no[rem_no] + sample_text[rem_text] + '\n')

    # terminal logging
    if i % 1000 == 0:
        print(str(i)+" recs done")

f.close()
print("File created.")