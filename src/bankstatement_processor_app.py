import bankstatement_processor_startup

def main():
    print("main")
    bankstatement_processor_startup.lambda_local_run()
    #bankstatement_processor_startup.store_server_details("test", "spot_test")

if __name__ == "__main__":
    main()