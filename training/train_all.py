from training.train_content import train_content
from training.build_user_profiles import build_user_profiles
from training.train_collaborative import train_collaborative


def train_all():
    print("[1/3] Training content model...")
    train_content()

    print("[2/3] Building user content profiles...")
    build_user_profiles()

    print("[3/3] Training collaborative model...")
    train_collaborative()

    print("Training finished. Artifacts are ready in ./artifacts")


if __name__ == "__main__":
    train_all()
