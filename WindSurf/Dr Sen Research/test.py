import torch
import numpy as np
import json
import os
import pickle
from itertools import count
import matplotlib.pyplot as plt
import glob

# Define the folder where you want to save your models and metrics
save_folder = "/content/drive/MyDrive/Trevor's_Research_results_Notes_and_Research_log/3. My_Models/Trained_Models/PC89-S6d-LargeMap-FullTraining-UnlimitedFunds/Training_2"

# Create the folder if it doesn't exist
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

def get_latest_episode():
    # Check for the existence of the checkpoint file
    checkpoint_path = os.path.join(save_folder, "dqn_policy_model_checkpoint.pth")
    if os.path.exists(checkpoint_path):
        # Load the metrics file to get the last episode number
        metrics_path = os.path.join(save_folder, "metrics_checkpoint.json")
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            return len(metrics['episode_avg_rewards'])
    return 0

def save_progress(episode):
    # Define base filenames without episode numbers
    policy_model_save_path = os.path.join(save_folder, "dqn_policy_model_checkpoint.pth")
    target_model_save_path = os.path.join(save_folder, "dqn_target_model_checkpoint.pth")
    metrics_save_path = os.path.join(save_folder, "metrics_checkpoint.json")
    steps_done_save_path = os.path.join(save_folder, "steps_done_checkpoint.json")
    replay_memory_save_path = os.path.join(save_folder, "replay_memory_checkpoint.pkl")
    optimizer_save_path = os.path.join(save_folder, "optimizer_checkpoint.pth")

    # Save the policy network
    torch.save(policy_net.state_dict(), policy_model_save_path)

    # Save the target network
    torch.save(target_net.state_dict(), target_model_save_path)

    # Save metrics
    with open(metrics_save_path, 'w') as f:
        json.dump({
            'episode_avg_rewards': episode_avg_rewards,
            'episode_losses': episode_losses
        }, f)

    # Save steps_done
    with open(steps_done_save_path, 'w') as f:
        json.dump({
            'steps_done': steps_done
        }, f)

    # Save replay memory
    with open(replay_memory_save_path, 'wb') as f:
        pickle.dump(memory, f)

    # Save optimizer state
    torch.save(optimizer.state_dict(), optimizer_save_path)

    print(f"Checkpoint updated at episode {episode}")

def load_progress():
    # Load from checkpoint files without episode numbers
    policy_model_load_path = os.path.join(save_folder, "dqn_policy_model_checkpoint.pth")
    target_model_load_path = os.path.join(save_folder, "dqn_target_model_checkpoint.pth")
    metrics_load_path = os.path.join(save_folder, "metrics_checkpoint.json")
    steps_done_load_path = os.path.join(save_folder, "steps_done_checkpoint.json")
    replay_memory_load_path = os.path.join(save_folder, "replay_memory_checkpoint.pkl")
    optimizer_load_path = os.path.join(save_folder, "optimizer_checkpoint.pth")

    try:
      # Load policy network
      policy_net.load_state_dict(torch.load(policy_model_load_path))

      # Load target network
      target_net.load_state_dict(torch.load(target_model_load_path))
    except:
      # Load policy network
      # Explicitly map the model to the CPU when loading
      policy_net.load_state_dict(torch.load(policy_model_load_path, map_location=torch.device('cpu')))

      # Load target network
      # Explicitly map the model to the CPU when loading
      target_net.load_state_dict(torch.load(target_model_load_path, map_location=torch.device('cpu')))


    # Load metrics
    with open(metrics_load_path, 'r') as f:
        metrics = json.load(f)
        global episode_avg_rewards, episode_losses
        episode_avg_rewards = metrics['episode_avg_rewards']
        episode_losses = metrics['episode_losses']

    # Load steps_done
    with open(steps_done_load_path, 'r') as f:
        steps_done_data = json.load(f)
        global steps_done
        steps_done = steps_done_data['steps_done']

    # Load replay memory
    with open(replay_memory_load_path, 'rb') as f:
        global memory
        memory = pickle.load(f)

    # Load optimizer state
    optimizer.load_state_dict(torch.load(optimizer_load_path))

    print(f"Checkpoint loaded")

# Check if there's a saved state to resume from
start_episode = get_latest_episode()
if start_episode > 0:
    load_progress()
    start_episode += 1  # Start from the next episode
else:
    start_episode = 0
    # Initialize your variables here (episode_avg_rewards, episode_losses, steps_done, memory)
    episode_avg_rewards = []
    episode_losses = []
    steps_done = 0
    memory = ReplayMemory(10000)  # Assuming you have a ReplayMemory class defined

additional_episode = 5000 #Should be 5000 for learning agents
end_episode = start_episode + additional_episode

# Initialize optimizer with initial learning rate
initial_LR = 0.000001  # Set your initial learning rate
optimizer = torch.optim.AdamW(policy_net.parameters(), lr=initial_LR)

def print_progress(episode, avg_reward, loss, actions_taken):
    print(f"Episode: {episode}")
    print(f"Average Reward: {avg_reward:.4f}")
    if loss is not None:
        print(f"Loss: {loss:.4f}")
    print("Actions Taken:")
    for action, count in actions_taken.items():
        print(f"  Action {action}: {count}")
    print("-" * 40)

for i_episode in range(start_episode, end_episode):
    # Initialize the environment and get its state
    state = env.reset()
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    rewards_in_episode = []
    losses_in_episode = []
    actions_taken = {}

    for t in count():
        action_mask = env.generate_mask()
        action_mask = torch.tensor(action_mask, dtype=torch.float32, device=device)
        action = select_action(state, action_mask)

        # Count actions taken
        action_item = action.item()
        actions_taken[action_item] = actions_taken.get(action_item, 0) + 1

        observation, reward, terminated, truncated, _ = env.step(action_item)
        rewards_in_episode.append(reward)
        reward = torch.tensor([reward], device=device)
        done = env.check_done()

        if terminated:
            next_state = None
        else:
            next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

        # Store the transition in memory
        memory.push(state, action, next_state, reward)

        state = next_state

        # Perform one step of the optimization (on the policy network)
        loss = optimize_model()
        if loss is not None:
            losses_in_episode.append(loss)

        # Soft update of the target network's weights
        target_net_state_dict = target_net.state_dict()
        policy_net_state_dict = policy_net.state_dict()
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
        target_net.load_state_dict(target_net_state_dict)

        if done:
            episode_durations.append(t+1)
            episode_avg_reward = np.mean(rewards_in_episode)
            episode_avg_rewards.append(episode_avg_reward)
            episode_loss = np.mean(losses_in_episode) if losses_in_episode else None
            if episode_loss is not None:
                episode_losses.append(episode_loss)

            # Print progress
            print_progress(i_episode, episode_avg_reward, episode_loss, actions_taken)

            break

    # Save progress every 50 episodes
    if (i_episode + 1) % 50 == 0:
        save_progress(i_episode + 1)
        print(f"Checkpoint updated at episode {i_episode + 1}")

env.print_final_action_counts()

# Final save after all episodes
save_progress(end_episode)
print(f"Training completed. Final checkpoint saved i.e. episode {end_episode}")

# Plot metrics
plot_metrics(show_result=True, save_format='svg', filename_prefix='10_closest_damaged_facilities_3_crews_58_budget_3')

plt.show()