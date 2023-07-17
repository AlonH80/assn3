from app import FoodApplication


def main():
    food_app = FoodApplication("config/config.yaml")
    food_app.setup_app()
    food_app.run_app()
    food_app.join_app()


if __name__ == '__main__':
    main()

