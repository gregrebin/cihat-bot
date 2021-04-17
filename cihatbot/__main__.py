from cihatbot.app import Application


def main():
    application = Application("cihatbot.local.cfg")
    application.add_user()
    application.run()


if __name__ == '__main__':
    main()

