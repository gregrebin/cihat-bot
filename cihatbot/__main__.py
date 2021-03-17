from cihatbot.app import Application


def main():
    print("Starting Cihat-traders")

    application = Application("telegram", "binance", "cihatbot.cfg")
    application.run()


if __name__ == '__main__':
    main()

