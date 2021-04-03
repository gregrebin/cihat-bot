from cihatbot.app import Application


def main():
    application = Application("cihatbot.cfg")
    application.add_user()
    application.run()


if __name__ == '__main__':
    main()

