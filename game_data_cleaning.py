import csv
import re

csv_reader = csv.reader(open("dataset/steam_games.csv", "r"))
f = open('new_steam_games.csv', 'w')
writer = csv.writer(f)
writer.writerow(['Positive', 'Negative', 'Game_name', 'Positive_Rate', 'Link'])
for i, line in enumerate(csv_reader):
    if i == 0:
        continue
    if line[5] != 'NaN' and 'Need more user reviews' not in line[5] and line[5] != '':
        p = re.compile(r'[(](.*)[)]', re.S)
        all_reviews = int(re.findall(p, line[5])[0].replace(",", ""))
        print(all_reviews)
        # print(re.findall(p, line[5]))
        p2 = re.findall(r'(\d+)%', line[5])
        rate = int(p2[0])/100
        print(rate)
        positive = int(all_reviews * rate)
        print(positive)
        negative = all_reviews - positive
        print(negative)
        url = line[0]
        print(url)
        # print(line[5])
        print(line[0].split('/')[-2].replace('_', ' ').strip())
        name = line[0].split('/')[-2].replace('_', ' ').strip()
        print(name)
        print(i)
        writer.writerow([positive, negative, name, rate, url])
f.close()
