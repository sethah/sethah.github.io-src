import numpy as np
import pandas as pd
import matplotlib.mlab as mlab


def gen_ratings(num_teams, seed=7):
    np.random.seed(seed)
    o = np.random.normal(0, 3, num_teams)
    d = np.random.normal(0, 3, num_teams)
    return o - np.mean(o), d - np.mean(d)

def gen_matchups(N, k, seed=7):
    np.random.seed(seed)
    return np.array([np.random.choice(range(k), 2, replace=False) for i in range(N)])

def construct_games(off_skill, def_skill, matchups, intercept, home, std):
    games_df = pd.DataFrame(matchups, columns=["Home Team", "Away Team"])
    games_df['Home Off. Skill'] = games_df['Home Team'].map(lambda i: off_skill[i])
    games_df['Home Def. Skill'] = games_df['Home Team'].map(lambda i: def_skill[i])
    games_df['Away Off. Skill'] = games_df['Away Team'].map(lambda i: off_skill[i])
    games_df['Away Def. Skill'] = games_df['Away Team'].map(lambda i: def_skill[i])
    games_df['E[Home]'] = games_df['Home Off. Skill'] + games_df['Away Def. Skill'] + intercept + home
    games_df['E[Away]'] = games_df['Away Off. Skill'] + games_df['Home Def. Skill'] + intercept - home
    games_df['Home Score'] = np.random.normal(games_df['E[Home]'].values, std)
    games_df['Away Score'] = np.random.normal(games_df['E[Away]'].values, std)
    return games_df

def construct_feature_df(games_df):
    feature_df1 = games_df[['Home Team', 'Away Team', 'Home Score']].copy()
    feature_df1.rename(columns={'Home Team': 'Off. Team', 'Away Team': 'Def. Team', 'Home Score': 'Score'}, inplace=True)
    feature_df1['Home'] = 1
    feature_df2 = games_df[['Home Team', 'Away Team', 'Away Score']].copy()
    feature_df2.rename(columns={'Away Team': 'Off. Team', 'Home Team': 'Def. Team', 'Away Score': 'Score'}, inplace=True)
    feature_df2['Home'] = -1
    feature_df = pd.concat([feature_df1, feature_df2], 0).sort_index().reset_index().drop('index', 1)
    return feature_df[['Off. Team', 'Def. Team', 'Home', 'Score']]

def constrained_dummies(dummies):
    N, k = dummies.shape
    subtract = np.array([np.zeros(k - 1) if dummies.values[i, -1] == 0 else np.ones(k - 1) for i in range(N)])
    return pd.DataFrame(dummies.values[:, :-1] - subtract, columns=dummies.columns[:-1])

def get_gaussian(mean, sigma):
    x = np.linspace(mean - 5 * sigma, mean + 5 * sigma, 100)
    return x, mlab.normpdf(x, mean, sigma)

def extract_coefs(res, k):
    sm_off_coefs = res.params[:k - 1]
    sm_off_coefs = np.append(sm_off_coefs, -1 * np.sum(sm_off_coefs))
    sm_def_coefs = res.params[k - 1:2 * (k - 1)]
    sm_def_coefs = np.append(sm_def_coefs, -1 * np.sum(sm_def_coefs))
    sm_intercept = res.params[-1]
    sm_home = res.params[-2]

    sm_cov = res.cov_params()
    sm_off_cov = sm_cov[:k-1, :k-1]
    sm_def_cov = sm_cov[k-1:2*(k-1), k-1:2*(k-1)]
    sm_off_sigmas = np.sqrt(np.append(sm_off_cov.diagonal(), np.sum(sm_off_cov)))
    sm_def_sigmas = np.sqrt(np.append(sm_def_cov.diagonal(), np.sum(sm_def_cov)))
    sm_intercept_sigma = np.sqrt(sm_cov[-1, -1])
    sm_home_sigma = np.sqrt(sm_cov[-2, -2])

    sm_ci = res.conf_int()
    sm_off_ci = sm_ci[:k - 1]
    sm_off_ci = np.append(sm_off_ci, [sm_off_coefs[-1] - sm_off_sigmas[-1] * 1.96, sm_off_coefs[-1] + sm_off_sigmas[-1] * 1.96])
    sm_def_ci = sm_ci[k - 1:2 * (k - 1)]
    sm_def_ci = np.append(sm_def_ci, [sm_def_coefs[-1] - sm_def_sigmas[-1] * 1.96, sm_def_coefs[-1] + sm_def_sigmas[-1] * 1.96])

    return {
        'coefs': {'off': sm_off_coefs, 'def': sm_def_coefs, 'home': sm_home, 'intercept': sm_intercept},
        'stds': {'off': sm_off_sigmas, 'def': sm_def_sigmas, 'home': sm_home_sigma, 'intercept': sm_intercept_sigma},
        'ci': {'off': sm_off_ci.reshape(k, 2), 'def': sm_def_ci.reshape(k, 2), 'home': sm_ci[-2], 'intercept': sm_ci[-1]}
        }

