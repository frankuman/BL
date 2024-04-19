def main():
    print("Running")
    from frontend import dashboard
    dashboard.app.run(host="127.0.0.1", debug=True)

if __name__ == "__main__":
    main()