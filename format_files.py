import os
import re


# Formats times into a csv friendly string, where the left column contains the
# time where a face was detected, and the right column contains when the face
# 'looked away'
def format_times_positive(times, faces, msg="Looked at cam,Looked away\nTimes looked,"):
    even = len(times) if len(times) % 2 == 0 else len(times) - 1
    result = "%s %s\nIntervals,(s)\n" % (msg, faces)
    for i in range(0, even, 2):
        result += "%s,%s\n" % (str(times[i]).strip(), str(times[i + 1]).strip())
    return result


# Does the same as format_times_positive, except the left column contains when a face
# looked away and the right column contains when it looked back.
def format_times_negative(times, faces):
    return format_times_positive(times[1:], faces - 1, "Looked away,Looked at cam\nTimes looked away,")


# Reads the analysis file, renames the last _flag, and writes the formatted csv file
def write_files(file_names, line_ending, positivep, in_dir, out_dir):
    func = format_times_positive if positivep else format_times_negative
    for f in file_names:
        lines = open(os.path.join(in_dir, f), 'r').readlines()
        target = open(os.path.join(out_dir, f.replace(f.split('_')[-1],
                                                      '%s.csv' % line_ending)), 'w')
        target.write(func(lines[:-1], int(lines[-1].split()[-1])))


# Effect: Searches for files that end with some flag (a flag is an _'flag'.txt)
# Then, it will create a formatted csv file, replacing the flag with "++" or "--" to
# denote whether it's for when faces look at camera or away from camera.
if __name__ == "__main__":
    in_dir = raw_input("Directory to parse? ")
    out_dir = "formatted"
    positive = re.compile(".*_%s.txt" % raw_input
                         ("Looking for positive matches in files ending with? "))
    negative = re.compile(".*_%s.txt" % raw_input
                         ("Looking for negative matches in files ending with? "))
    files = os.listdir(in_dir)
    print "Formatting positive files"
    write_files(filter(positive.match, files), '++', True, in_dir, out_dir)
    print "Formatting negative files"
    write_files(filter(negative.match, files), '--', False, in_dir, out_dir)
    print "All done!"
