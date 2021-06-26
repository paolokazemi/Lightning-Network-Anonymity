import ast
import nested_dict as nd
import matplotlib.pyplot as plt
import numpy as np
import json
import seaborn as sns
import networkx as nx
import populate_graph as pg
import sys

# USAGE: python3 results.py <demo100 | demo500 | demo1000 | erdos500 | erdos1000 | snapshot> <file | results/results.json>

# Example: python3 results.py demo500 results/barabasi_albert_500.json
#    Prints results for demo500 graph using transactions found in results/barabasi_albert_500.json

# Example: python3 results.py demo1000 results/barabasi_albert_1000.json
#    Prints results for demo1000 graph using transactions found in results/barabasi_albert_1000.json

# Example: python3 results.py erdos500 results/erdos_renyi_500.json
#    Prints results for erdos500 graph using transactions found in results/erdos_renyi_500.json

# Example: python3 results.py erdos1000 results/erdos_renyi_1000.json
#    Prints results for erdos1000 graph using transactions found in results/erdos_renyi_1000.json

# Example: python3 results.py snapshot results/snapshot.json
#    Prints results for the LN snapshot graph using transactions found in results/snapshot.json

# Example: python3 results.py snapshot
#    Prints results for the LN snapshot graph using transactions found in results/results.json

file = "results/results.json" if len(sys.argv) < 3 else sys.argv[2]

# Open the results file and transfer the in an array
results = []
with open(file,'r') as json_file:
    results_json = json.load(json_file)
results.append(results_json)


path = []

# Number of Transactions
num_transactions = 0

# Number of transactions attacked
num_attacked = 0

# Total number of attack instances
num_attacks = 0

# Array storing the number of recipients for each attack instance, followed by those that that had phase I completed and not respectively
dest_count = []
dest_count_comp = []
dest_count_incomp = []

# Arrays storing the number of senders for each attack instance, followed by those that that had phase I completed and not respectively
source_count = []
source_count_comp = []
source_count_incomp = []

# Arrays storing the distances of the recipient and the sender from the adversary respectively
dist_dest = []
dist_source = []

# Number of attack instances in which the sender and recipient pair was successfully found
pair_found = 0

# Number of attack instances that completed phase I
num_comp = 0

# Number of attack instances for which the size of the recipient set was 1 and similarly for the sender
sing_dest = 0
sing_source = 0

# Number of attack instances having both the sender and recipient sets singular
sing_all = 0

# Number of attack instances having atleast one of the sender and recipient sets singular
sing_any = 0

if len(sys.argv) > 1:
    if sys.argv[1] == 'demo100':
        # DEMO: 100 2 65
        ads = [3, 2, 7, 25, 5, 1, 11, 10, 6, 15]
    elif sys.argv[1] == 'demo500':
        # DEMO: 500 5 65
        ads = [5, 18, 8, 7, 6, 3, 10, 11, 1, 13]
    elif sys.argv[1] == 'demo1000':
        # DEMO: 1000 8 65
        ads = [9, 10, 8, 14, 11, 16, 20, 12, 13, 18]
    elif sys.argv[1] == 'snapshot':
        # Snapshot Adversaries
        ads = [2634, 8075, 5347, 1083, 5093,4326, 4126, 2836, 5361, 10572,5389, 3599, 9819, 4828, 3474, 8808, 93, 9530, 9515, 2163]
        # ads = [14727, 15627, 6028, 14362, 10397, 6945, 804, 7588, 2344, 4905, 8499, 4278, 9274, 15291, 13114, 10577, 1746, 853, 86, 5346, 13426, 2163]
    elif sys.argv[1] == 'erdos500':
        ads = [417, 322, 12, 20, 278, 370, 444, 35, 102, 212]
    elif sys.argv[1] == 'erdos1000':
        ads = [17, 618, 730, 491, 438, 241, 948, 161, 906, 903]
    else:
        # DEMO: 100 2 65
        ads = [3, 2, 7, 25, 5, 1, 11, 10, 6, 15]
else:
    # DEMO: 100 2 65
    ads = [3, 2, 7, 25, 5, 1, 11, 10, 6, 15]

# Dictionary for storing the number of attack instances of each adversary
ad_attacks = {}
for ad in ads:
    ad_attacks[ad] = 0

# Hop counts per transaction
hop_count = []

# False positives
false_positive_source = 0
false_positive_dest = 0
false_positive_any = 0
false_positive_all = 0

# Deanonymized
found_sources = 0
found_destinations = 0
found_both = 0

# Fees
fees = []
fees_normalized = []

# Failed transactions
failed_transactions = 0

# Go over the results and update each of the above variables for each attack instance
for i in results if type(results) == list else [results]:
    for j in i if type(i) == list else [i]:
        for k in j if type(j) == list else [j]:
            if k["path"]!=path:
                path = k["path"]
                num_transactions+=1
                if not k["success"]:
                    failed_transactions += 1
                hop_count.append(len(path) - 2) # Remove sender and receiver
                fees.append(k["Cost"] - k["amount"])
                fees_normalized.append((k["Cost"] - k["amount"]) / k["amount"])
                if k["attacked"]>0:
                    num_attacked+=1
                    anon_sets = k["anon_sets"]
                    for ad in anon_sets:
                        num_attacks+=1
                        num = -1
                        for adv in ad:
                            sources = []
                            destinations = []
                            ad_attacks[int(adv)]+=1
                            num+=1
                            for dest in ad[adv]:
                                for rec in dest:
                                    if len(dest[rec]) > 0:
                                        destinations.append(int(rec))
                                    isSourceFound = False
                                    for tech in dest[rec]:
                                        if len(sys.argv) > 1 and sys.argv[1] == 'snapshot':
                                            for s in dest[rec][tech]:
                                                if s == k["sender"]:
                                                    isSourceFound = True
                                                sources.append(s)
                                        else:
                                            if tech == k["sender"]:
                                                isSourceFound = True
                                            sources.append(tech)
                                    if int(rec) == k["recipient"] and isSourceFound:
                                        pair_found += 1
                            if len(set(sources))>0:
                                ind = k["path"].index(int(adv))
                                dist_dest.append(len(k["path"])-1-ind)
                                dist_source.append(ind)
                                if (k["comp_attack"][num] == 1):
                                        num_comp+=1

                                # Excluding false positives
                                if not (len(ad[adv]) == 1 and destinations[0] != k["recipient"]):
                                    if(k["comp_attack"][num] == 1):
                                        dest_count_comp.append(len(ad[adv]))
                                    else:
                                        dest_count_incomp.append(len(ad[adv]))
                                dest_count.append(len(ad[adv]))
                                if(len(ad[adv]) == 1):
                                    sing_dest+=1
                                    if destinations[0] != k["recipient"]:
                                        false_positive_dest += 1
                                    else:
                                        found_destinations += 1

                                # Excluding false positives
                                if not (len(set(sources))==1 and sources[0] != k["sender"]):
                                    if (k["comp_attack"][num] == 1):
                                        source_count_comp.append(len(set(sources)))
                                    else:
                                        source_count_incomp.append(len(set(sources)))
                                source_count.append(len(set(sources)))
                                if(len(set(sources))==1):
                                    sing_source+=1
                                    if sources[0] != k["sender"]:
                                        false_positive_source += 1
                                    else:
                                        found_sources += 1
                                if(len(ad[adv]) ==1) or (len(set(sources))==1):
                                    sing_any+=1
                                    if (len(destinations) == 1 and destinations[0] != k["recipient"]) or (len(set(sources)) == 1 and sources[0] != k["sender"]):
                                        false_positive_any += 1
                                if (len(ad[adv]) == 1) and (len(set(sources)) == 1):
                                    sing_all += 1
                                    if destinations[0] != k["recipient"] and sources[0] != k["sender"]:
                                        false_positive_all += 1
                                    elif destinations[0] == k["recipient"] and sources[0] == k["sender"]:
                                        found_both += 1


def perc(num):
    return round(num * 100, 2)

def percent(num, den):
    return str(perc(num / den) if den != 0 else 0.00) + '%'

def ratio(num, den):
    return round(num / den, 2) if den != 0 else 0.00

# Print the metrics
print(f'Transactions: {num_transactions}')
print(f'Failed Transactions: {failed_transactions}')
print(f'Transactions attacked: {num_attacked}')
print(f'Attacks: {num_attacks}')
print(f'Pairs found: {pair_found}')
# print(f'Sources found per attack: {source_count}')
# print(f'Destinations found per attack: {dest_count}')
# print(f'Hop counts per transaction: {hop_count}')
print()

attack_transaction_ratio = num_attacked/num_transactions if num_transactions != 0 else 0
attack_attacked_ratio = num_attacks/num_attacked if num_attacked != 0 else 0
print(f'Attacked/Transactions ratio: {attack_transaction_ratio} ({perc(attack_transaction_ratio)}%)')
print(f'Attacks/Attacked ratio: {attack_attacked_ratio} ({perc(attack_attacked_ratio)}%)')
print('Correlation destination to distance\n', np.corrcoef(dest_count,dist_dest))
print('Correlation source to distance\n',np.corrcoef(source_count,dist_source))
print()

sing_source_ratio = sing_source/num_attacks if num_attacks != 0 else 0
sing_dest_ratio = sing_dest/num_attacks if num_attacks != 0 else 0
sing_any_ratio = sing_any/num_attacks if num_attacks != 0 else 0
sing_all_ratio = sing_all/num_attacks if num_attacks != 0 else 0
complete_one_attack_ratio = num_comp/num_attacks if num_attacks != 0 else 0
print(f'Singular sources ratio: {sing_source_ratio} ({perc(sing_source_ratio)}%)')
print(f'Singular destination ratio: {sing_dest_ratio} ({perc(sing_dest_ratio)}%)')
print(f'Singular source or destination ratio: {sing_any_ratio} ({perc(sing_any_ratio)}%)')
print(f'Both Singular ratio: {sing_all_ratio} ({perc(sing_all_ratio)}%)')
print(f'Complete I phase ratio: {complete_one_attack_ratio} ({perc(complete_one_attack_ratio)}%)')
print(f'Average number of hop counts: {sum(hop_count) / len(hop_count) if len(hop_count) != 0 else 0}')
print(f'Average fee: {sum(fees) / len(fees) if len(fees) != 0 else 0}')
print()

false_positive_source_ratio = false_positive_source / num_attacks if num_attacks != 0 else 0
false_positive_dest_ratio = false_positive_dest / num_attacks if num_attacks != 0 else 0
false_positive_any_ratio = false_positive_any / num_attacks if num_attacks != 0 else 0
false_positive_all_ratio = false_positive_all / num_attacks if num_attacks != 0 else 0
print(f'False positive sources ratio: {false_positive_source_ratio} ({perc(false_positive_source_ratio)}%)')
print(f'False positive destination ratio: {false_positive_dest_ratio} ({perc(false_positive_dest_ratio)}%)')
print(f'False positive source or destination ratio: {false_positive_any_ratio} ({perc(false_positive_any_ratio)}%)')
print(f'False positive sources and destination ratio: {false_positive_all_ratio} ({perc(false_positive_all_ratio)}%)')
print()

sources_found = found_sources / num_attacks if num_attacks != 0 else 0
destinations_found = found_destinations / num_attacks if num_attacks != 0 else 0
found_pairs = pair_found / num_attacks if num_attacks != 0 else 0
both_found = found_both / num_attacks if num_attacks != 0 else 0
print(f'Found singular sources: {sources_found} ({perc(sources_found)}%)')
print(f'Found singular destinations: {destinations_found} ({perc(destinations_found)}%)')
print(f'Found both: {found_pairs} ({perc(found_pairs)}%)')
print(f'Found both singular: {both_found} ({perc(both_found)}%)')
print()

print(f'''
STATS:
Failed transactions:                {percent(failed_transactions, num_transactions)}
Average number of hop counts:       {round(sum(hop_count) / len(hop_count), 2) if len(hop_count) != 0 else 0}
Average fee:                        {round(sum(fees) / len(fees), 2) if len(fees) != 0 else 0}

Singular sources:                   {percent(found_sources, num_attacks)}
Singular destinations:              {percent(found_destinations, num_attacks)}
Singular both:                      {percent(found_both, num_attacks)}
Pairs found:                        {percent(pair_found, num_attacks)}
''')

print(f'''
\\( R_{{att}} \\) & {ratio(num_attacked, num_transactions)} \\\\
\\( Av_{{att}} \\) & {ratio(num_attacks, num_attacked)} \\\\
\\( CorrD_S \\) & {round(np.corrcoef(source_count,dist_source)[0][1], 2)} \\\\
\\( CorrD_R \\) & {round(np.corrcoef(dest_count,dist_dest)[0][1], 2)} \\\\
\\( Sing_S \\) & {ratio(found_sources, num_attacks)} \\\\
\\( Sing_R \\) & {ratio(found_destinations, num_attacks)} \\\\
\\( Sing_{{Both}} \\) & {ratio(found_both, num_attacks)} \\\\
\\( Comp_{{I}} \\) & {ratio(num_comp, num_attacks)} \\\\
\\( Success_{{att}} \\) & {ratio(pair_found, num_attacks)} \\\\
\\( FalsePos_S \\) & {ratio(false_positive_source, num_attacks)} \\\\
\\( FalsePos_R \\) & {ratio(false_positive_dest, num_attacks)} \\\\
\\( FalsePos_{{Both}} \\) & {ratio(false_positive_all, num_attacks)} \\\\
\\( Fail \\) & {ratio(failed_transactions, num_transactions)} \\\\
\\( Av_{{hop}} \\) & {round(sum(hop_count) / len(hop_count), 2) if len(hop_count) != 0 else 0} \\\\
\\( Av_{{fee}} \\) & {round(sum(fees) / len(fees), 2) if len(fees) != 0 else 0} \\\\
\\( N_{{fee}} \\) & {round(sum(fees_normalized) / len(fees_normalized), 2) if len(fees_normalized) != 0 else 0} \\\\
''')

if len(dest_count_comp) == 0 or len(dest_count_incomp) == 0 or len(source_count_comp) == 0 or len(source_count_incomp) == 0:
    exit(0)

# Plot the sender and recipient anonymity sets respectively
plot1 = sns.ecdfplot(data = dest_count_comp,legend='Phase I complete',marker = '|',linewidth = 3.5, linestyle = '-')
plot2 = sns.ecdfplot(data = dest_count_incomp,legend='Phase I incomplete',marker = '|',linewidth = 3.5, linestyle = '-')
plot1.set(xscale='log')
plot2.set(xscale='log')
plt.legend(('Phase I complete','Phase I incomplete'),scatterpoints=1,loc='lower right',ncol=1,fontsize=16)
plt.xlabel("Size of anonymity set")
plt.ylabel("CDF")
plt.show()
plt.savefig('results/dest.jpg')

plt.clf()

plot1 = sns.ecdfplot(data = source_count_comp,legend='Phase I complete',marker = '|',linewidth = 3.5, linestyle = '-')
plot2 = sns.ecdfplot(data = source_count_incomp,legend='Phase I incomplete',marker = '|',linewidth = 3.5, linestyle = '-')
plot1.set(xscale='log')
plot2.set(xscale='log')
plt.legend(('Phase I complete','Phase I incomplete'),scatterpoints=1,loc='lower right',ncol=1,fontsize=16)
plt.xlabel("Size of anonymity set")
plt.ylabel("CDF")
plt.show()
plt.savefig('results/source.jpg')
