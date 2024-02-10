# Datastreamer standalone entry point
# Spec @ https://github.com/orgs/ISSUIUC/projects/4/views/1?pane=issue&itemId=52868143

# Implement standalone datastreamer functionality
# Implement new state machine
# Add ability to write to this directory (or `./output`) after runs finish.
# Reuse as much of the already written code as possible.

def main():
    pass

if __name__ == "__main__":
    main()
else:
    print("Datastreamer standalone must be run as the entry point. It cannot be imported.")
    exit(1)