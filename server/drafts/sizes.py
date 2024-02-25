from sudachipy import Dictionary
from matplotlib import pyplot as plt
import os


def get_tokens(tokenizer, text, start):
    X = []
    my_sizes_before = []
    sudachi_sizes = []
    my_sizes_after = []
    differences = []
    n = len(text)
    for i in range(start, n, 1):
        string = text[:i + 1]
        attrs_before = get_attrs(string)
        try:
            size_before = string.__sizeof__()
            tokenizer.tokenize(string)
        except Exception as ex:
            X.append(i)
            ex = str(ex).split()
            try:
                sudachi_sizes.append(int(ex[-1]))
            except:
                print(ex)
            my_sizes_before.append(size_before)
            my_sizes_after.append(string.__sizeof__())
            differences.append(my_sizes_after[-1] - size_before)
            if i == start:
                print('!!!!!!!!!!!!!!')
            unmatched = [(i, j) for i, j in zip(attrs_before, get_attrs(string)) if i != j]
            print('length:', i + 1, 'before:', size_before, 'after:', my_sizes_after[-1], 'sudachi:', sudachi_sizes[-1], )
            break
        #os.system('cls')
        #print(f'{i / n:0.2f}')
    # plt.title('Depepndance of string sizes in bytes on the string length')
    # for label, values in {
    #     'differences between the value of\nstring.__sizeof__() gotten after and before exception': differences,
    #     'value of string.__sizeof__()\ngotten before the exception': my_sizes_before,
    #     'size from SudachiPy exception': sudachi_sizes, 
    #     'value of string.__sizeof__()\ngotten after the exception': my_sizes_after, 
    #     }.items():
    #     plt.plot(X, values, label=label)
    # plt.gca().lines[3].set_linestyle('dotted')
    # plt.gca().lines[2].set_linestyle('dashed')
    # plt.gca().lines[1].set_linestyle('dashdot')
    # plt.legend()
    # plt.show()

    # for i, j, o in zip(my_sizes_before, my_sizes_after, sudachi_sizes):
    #     if j - i - o != 1:
    #         #print(j - i - o)
    #         pass

def get_attrs(obj):
    attrs = []
    for name in dir(obj):
        try:
            attrs.append([name, getattr(obj, name)()])
        except:
            attrs.append([name, getattr(obj, name)])
    return attrs

text = open('text_example.txt', encoding='utf-8').read()

print('max:', 49149)
for i, j in zip([text, '1' * 100_000, 'は' * 100_000], [20798, 49198, 16398]):
    get_tokens(Dictionary().create(), i, j - 200)


