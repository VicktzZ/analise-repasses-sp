test = "test"

def test():
    print(test)

if __name__ == "__main__":
    test()
    print("test")

uvicorn = "test:app --reload"
uvicorn.run()