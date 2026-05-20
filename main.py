import sys

from generator import generate_post

if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]).strip() or input("Тема поста: ")
    post = generate_post(topic)
    print("\n" + "=" * 50)
    print(post)
    print("=" * 50)
