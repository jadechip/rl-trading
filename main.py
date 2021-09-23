import gym
import json
import datetime as dt

from stable_baselines.common.policies import MlpPolicy, MlpLnLstmPolicy
from stable_baselines.common.vec_env import SubprocVecEnv, DummyVecEnv
from stable_baselines import A2C, ACKTR, PPO2

from env.BitcoinTradingEnv import StockTradingEnv
import pandas as pd

df = pd.read_csv('./data/BTCUSDT-1m-data.csv')
df = df.sort_values('Date')

# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: StockTradingEnv(df)])


model = PPO2(MlpLnLstmPolicy, train_env, verbose=0, nminibatches=1,
            tensorboard_log="./tensorboard", **model_params)

model.learn(total_timesteps=20000)

obs = env.reset()
for i in range(2000):
  action, _states = model.predict(obs)
  obs, rewards, done, info = env.step(action)
  env.render()


# while True:
#     action, state = model.predict(zero_completed_obs, state=state)
#     obs, reward, done, info = trade_env.step([action[0]])

#     zero_completed_obs[0, :] = obs

#     rewards.append(reward)

#     if done:
#         net_worths = pd.DataFrame({
#             'Date': info[0]['timestamps'],
#             'Balance': info[0]['net_worths'],
#         })

#         net_worths.set_index('Date', drop=True, inplace=True)
#         returns = net_worths.pct_change()[1:]

#         if render_report:
#             qs.plots.snapshot(returns.Balance, title='RL Trader Performance')

#         if save_report:
#             reports_path = path.join('data', 'reports', f'{self.study_name}__{model_epoch}.html')
#             qs.reports.html(returns.Balance, file=reports_path)