import bankstatement_processor_startup
import bankstatement_processor_shutdown

def main():
    print("main")
    #bankstatement_processor_startup.lambda_local_run()
    #bankstatement_processor_startup.store_server_details("test", "spot_test")
    bankstatement_processor_shutdown.lambda_local_run()

if __name__ == "__main__":
    main()
