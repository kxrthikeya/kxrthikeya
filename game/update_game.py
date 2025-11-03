import json
import os
import re

def check_winner(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontal
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Vertical
        [0, 4, 8], [2, 4, 6]             # Diagonal
    ]
    for line in lines:
        a, b, c = line
        if board[a] and board[a] == board[b] and board[a] == board[c]:
            return board[a]
    if all(cell is not None for cell in board):
        return "Draw"
    return None

def generate_readme(game_state):
    board = game_state['board']
    status = game_state['status']
    next_player = game_state['next_player']
    
    # Generate the board table
    readme = "### Community Tic-Tac-Toe\n\n"
    if status == 'in_progress':
        readme += f"**It's {next_player}'s turn!** Click a square to make your move.\n\n"
    elif status == 'win':
        winner = check_winner(board)
        readme += f"**Game Over! {winner} wins!**\n\n"
    elif status == 'draw':
        readme += f"**Game Over! It's a draw!**\n\n"

    readme += "| | | |\n|---|---|---|\n"
    for i in range(0, 9, 3):
        row = "|"
        for j in range(3):
            cell_index = i + j
            if board[cell_index]:
                row += f" {board[cell_index]} |"
            elif status == 'in_progress':
                issue_title = f"tic-tac-toe|move|{cell_index}"
                issue_link = f"https://github.com/kxrthikeya/kxrthikeya/issues/new?title={issue_title}&body=Just+push+'Submit+new+issue'!"
                row += f" [ ]({issue_link}) |"
            else:
                row += "   |"
        readme += row + "\n"

    # Add move history
    readme += "\n### Last Moves\n\n| Player | Move |\n|---|---|\n"
    for move in reversed(game_state['moves'][-5:]): # Show last 5 moves
        readme += f"| @{move['player']} | {move['move']} |\n"

    return readme

def main():
    issue_title = os.getenv('ISSUE_TITLE')
    player = os.getenv('PLAYER')

    with open('game/game_state.json', 'r') as f:
        game_state = json.load(f)

    # Extract move from issue title
    match = re.match(r"tic-tac-toe\|move\|(\d)", issue_title)
    if not match:
        print("Not a valid game move issue.")
        return

    cell_index = int(match.group(1))
    
    # Update board
    if game_state['board'][cell_index] is None and game_state['status'] == 'in_progress':
        current_player = game_state['next_player']
        game_state['board'][cell_index] = current_player
        game_state['moves'].append({"player": player, "move": f"{current_player} to cell {cell_index}"})
        
        # Check for winner or draw
        winner = check_winner(game_state['board'])
        if winner == "Draw":
            game_state['status'] = 'draw'
        elif winner:
            game_state['status'] = 'win'
        else:
            game_state['next_player'] = 'O' if current_player == 'X' else 'X'

        # Write back the updated game state
        with open('game/game_state.json', 'w') as f:
            json.dump(game_state, f, indent=4)
        
        # Generate and write the new README
        new_readme = generate_readme(game_state)
        with open('README.md', 'w') as f:
            f.write(new_readme)

if __name__ == "__main__":
    main()
