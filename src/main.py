from traceback import print_exc
import sys

from game_state import GameState
from gui.app import GameApp


def _read_player_name() -> str | None:
    if len(sys.argv) > 1:
        value = " ".join(sys.argv[1:]).strip()
        return value or None
    return None


def main():
    try:
        game_state = GameState()
        player_name = _read_player_name()
        if player_name is not None:
            game_state.set_player_name(player_name)
        app = GameApp(game_state, player_name=player_name)
        app.mainloop()
    except Exception:
        print_exc()
        raise


if __name__ == "__main__":
    main()
