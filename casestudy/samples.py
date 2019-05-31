"""
Create several files from one file with Steam reviews

Samples file small files with a given number of rows from the original data and
writes the remaining data to sample0.

"""

import pandas as pd

num_small_files = 10
small_file_nrows = 100000

df = pd.read_csv('../data/steam.csv',
                 names=['game_id', 'review', 'sentiment', 'helpful'])

df['review_id'] = list(range(1, df.shape[0] + 1))
df['review_length'] = df.review.apply(lambda x: len(str(x)))

df = df[['review_id', 'game_id', 'review', 'review_length', 'sentiment', 'helpful']]

for i in range(num_small_files):
    sample = df.sample(small_file_nrows, random_state=4711 + i)
    sample.to_csv(f'./data/reviews.sample{i+1}.csv',
                  index=False,
                  encoding='utf-8')
    df = df[~df.review_id.isin(sample.review_id)]

df.to_csv(f'./data/reviews.sample0.csv',
          index=False,
          encoding='utf-8')
