import gsheets


def delete_token_file() -> bool:
    if gsheets.TOKEN_PATH.exists():
        gsheets.TOKEN_PATH.unlink()
        print(f"Deleted {gsheets.TOKEN_PATH} because Google authentication failed.")
        return True

    print(f"{gsheets.TOKEN_PATH} does not exist; starting authentication.")
    return False


def main():
    result = delete_token_file()
    
    if result:
        gsheets.main()


if __name__ == "__main__":
    main()
