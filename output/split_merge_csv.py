import os, re, sys


def split(data, n, prefix='', header=True, outpath='./'):
    print('Splitting files.')
    lines = data.split('\n')
    if header:
        header_line = lines[0]
        lines = lines[1:]
    lines_per_file = len(lines) // n + 1
    for i in range(1, n + 1):
        lines_to_write = []
        if header:
            lines_to_write.append(header_line)
        lines_to_write.extend(lines[(i - 1) * lines_per_file : i * lines_per_file])
        with open(os.path.join(outpath, '{}{}.csv'.format(prefix, i)), 'w') as f:
            f.write('\n'.join(lines_to_write))

def merge(infile_names, outfile_name, header=True, inpath='./', outpath='./'):
    print('Merging files.')
    outfile = open(os.path.join(outpath, outfile_name), 'w')
    flag = False
    for infile_name in infile_names:
        with open(os.path.join(inpath, infile_name), 'r') as infile:
            data = infile.read()
            lines = data.split('\n')
        if flag:
            outfile.write('\n'.join(lines[1:]))
        if not header or not flag:
            outfile.write(data)
            flag = True
        outfile.write('\n')
    outfile.close()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        files = []
        for file in os.listdir('./'):
            if file.endswith('.csv'):
                files.append(file)
        if '_' in files[0]:
            outfile_name = files[0].split('_')[0]
            nums = []
            for file in files:
                if '{}_'.format(outfile_name) in file:
                    nums.append(int(re.findall(r'(?<=_)\d+', file)[0]))
            infile_names = []
            for i in range(1, max(nums) + 1):
                if i not in nums:
                    print('Missing part {}.'.format(i))
                else:
                    infile_names.append('{}_{}.csv'.format(outfile_name, i))
            merge(infile_names, '{}.csv'.format(outfile_name))
        else:
            with open(files[0], 'r') as f:
                data = f.read()
            split(data, 10, prefix=files[0][:-4] + '_')
    else:
        mode = sys.argv[1]
        if mode == 'split':
            infile_path = sys.argv[2]
            n = int(sys.argv[3])
            with open(infile_path, 'r') as f:
                data = f.read()
            split(data, n, prefix=infile_path[:-4] + '_')
        if mode == 'merge':
            outfile_name = sys.argv[2]
            n = int(sys.argv[3])
            infile_names = ['{}_{}.csv'.format(outfile_name, i) for i in range(1, n + 1)]
            merge(infile_names, '{}.csv'.format(outfile_name))
