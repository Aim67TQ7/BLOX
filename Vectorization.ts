import streamlit as st; // Importing Streamlit to create the web app
import * as pd from 'pandas'; // Importing Pandas library for data manipulation
import { processDocuments, getFileSize } from './documentProcessor'; // Importing custom functions for processing documents
import { registerCompany, verifyLicense, storeVector } from './database'; // Importing database functions for user and data handling
import * as os from 'os'; // Importing OS module for handling file paths
import * as np from 'numpy'; // Importing Numpy for numerical computations
import * as tempfile from 'tempfile'; // Importing Tempfile to handle temporary files

st.setPageConfig({ // Setting up the app's configuration
    page_title: "Document Vectorizer", // Title of the app
    page_icon: "\uD83D\uDCC4", // Icon for the app
    layout: "wide" // Setting the layout to wide
});

function formatSize(sizeBytes: number): string { // Function to format file sizes into readable units
    const units = ['B', 'KB', 'MB', 'GB']; // Units of measurement for file sizes
    let size = sizeBytes; // Starting size in bytes
    for (const unit of units) { // Loop through each unit
        if (size < 1024.0) { // Check if size is less than 1024
            return `${size.toFixed(2)} ${unit}`; // Return size with the current unit
        }
        size /= 1024.0; // Convert size to the next unit
    }
    return `${size.toFixed(2)} TB`; // Return size in terabytes if very large
}

function main() { // Main function that runs the app
    st.title("\uD83D\uDCC4 Document Vectorizer"); // Display the app's title

    // Initialize session states
    if (!st.sessionState['licenseActivated']) { // Check if the license is activated
        st.sessionState['licenseActivated'] = false; // Initialize as false if not set
    }
    if (!st.sessionState['userRegistered']) { // Check if the user is registered
        st.sessionState['userRegistered'] = false; // Initialize as false if not set
    }
    if (!st.sessionState['companyLicense']) { // Check if the company license is set
        st.sessionState['companyLicense'] = null; // Initialize as null if not set
    }
    if (!st.sessionState['authenticated']) { // Check if the user is authenticated
        st.sessionState['authenticated'] = false; // Initialize as false if not set
    }
    if (!st.sessionState['showRegister']) { // Check if the register form is displayed
        st.sessionState['showRegister'] = false; // Initialize as false if not set
    }

    // Step 1: Authentication
    if (!st.sessionState['authenticated']) { // If the user is not authenticated
        st.header("Login/Register"); // Display the login/register header

        const [col1, col2] = st.columns(2); // Create two columns for login and register buttons
        if (col1.button("Login")) { // If login button is clicked
            st.sessionState['showRegister'] = false; // Show login form
        }
        if (col2.button("Register")) { // If register button is clicked
            st.sessionState['showRegister'] = true; // Show register form
        }

        if (st.sessionState['showRegister']) { // If register form is displayed
            const form = st.form("registerForm"); // Create a register form
            const email = form.textInput("Email"); // Input field for email
            const password = form.textInput("Set Password", { type: "password" }); // Input field for password
            const verifyPassword = form.textInput("Verify Password", { type: "password" }); // Input field to verify password

            if (form.formSubmitButton("Register")) { // If register form is submitted
                if (password === verifyPassword) { // Check if passwords match
                    const auth = new UserAuth(supabase); // Create a UserAuth instance
                    const result = auth.registerUser(email, password); // Register the user
                    if (result.success) { // If registration is successful
                        st.success("Registration successful! Please login."); // Show success message
                        st.sessionState['showRegister'] = false; // Hide register form
                    } else {
                        st.error(`Registration failed: ${result.error}`); // Show error message
                    }
                } else {
                    st.error("Passwords do not match"); // Show error if passwords don't match
                }
            }
        } else {
            const form = st.form("loginForm"); // Create a login form
            const email = form.textInput("Email"); // Input field for email
            const password = form.textInput("Password", { type: "password" }); // Input field for password

            if (form.formSubmitButton("Login")) { // If login form is submitted
                const auth = new UserAuth(supabase); // Create a UserAuth instance
                if (auth.verifyPassword(email, password)) { // Verify user credentials
                    st.sessionState['authenticated'] = true; // Mark user as authenticated
                    st.experimentalRerun(); // Reload the app
                } else {
                    st.error("Invalid email or password"); // Show error message
                }
            }
        }
        st.stop(); // Stop execution if user is not authenticated
    }

    // Step 2: License Activation
    if (!st.sessionState['licenseActivated']) { // If the license is not activated
        st.header("License Activation"); // Display the license activation header
        const form = st.form("licenseForm"); // Create a license form
        const licenseNumber = form.textInput("Enter License Number"); // Input field for license number
        if (form.formSubmitButton("Activate License")) { // If license form is submitted
            if (verifyLicense(licenseNumber)) { // Verify the license number
                st.sessionState['licenseActivated'] = true; // Mark license as activated
                st.sessionState['companyLicense'] = licenseNumber; // Store the license number
                st.success("License activated successfully!"); // Show success message
                st.experimentalRerun(); // Reload the app
            } else {
                st.error("Invalid or inactive license number"); // Show error message
            }
        }
        st.stop(); // Stop execution if license is not activated
    }

    // Step 3: Company Registration
    if (!st.sessionState['userRegistered']) { // If the user is not registered
        st.header("Complete Registration"); // Display the registration header
        const form = st.form("registrationForm"); // Create a registration form
        const companyName = form.textInput("Company Name"); // Input field for company name
        const location = form.textInput("Company Location"); // Input field for company location
        const contactEmail = form.textInput("Contact Email"); // Input field for contact email
        const phone = form.textInput("Phone Number"); // Input field for phone number

        if (form.formSubmitButton("Complete Registration")) { // If registration form is submitted
            const result = registerCompany(companyName, contactEmail, phone, location); // Register the company
            if (result.success) { // If registration is successful
                st.sessionState['userRegistered'] = true; // Mark user as registered
                st.success("Registration completed successfully!"); // Show success message
                st.experimentalRerun(); // Reload the app
            } else {
                st.error(`Registration failed: ${result.error}`); // Show error message
            }
        }
        st.stop(); // Stop execution if user is not registered
    }

    // Main Application
    st.write("Upload multiple documents to convert them into vector representations and export as CSV/NPY."); // Display the main app description

    // File size monitoring
    const [col1, col2] = st.columns(2); // Create two columns for displaying file size info
    const currentSize = getFileSize(); // Get the current file size
    const maxSize = 20 * 1024 * 1024; // 20MB as the maximum file size
    const progress = Math.min((currentSize / maxSize) * 100, 100); // Calculate progress percentage

    col1.write("NPY File Size"); // Label for file size progress
    col1.progress(progress / 100); // Display progress bar
    col1.write(`Current size: ${formatSize(currentSize)} / ${formatSize(maxSize)}`); // Display current and max file size

    // File uploader
    const uploadedFiles = st.fileUploader("Upload your documents", { // Create file uploader
        type: ["txt", "pdf", "doc", "docx"], // Allowed file types
        acceptMultipleFiles: true // Allow multiple files to be uploaded
    });

    if (uploadedFiles) { // If files are uploaded
        st.write(`\uD83D\uDCCE ${uploadedFiles.length} files uploaded`); // Display the number of uploaded files

        if (st.button("Process Documents")) { // If process button is clicked
            const progressBar = st.progress(0); // Initialize a progress bar
            const statusText = st.empty(); // Create an empty text placeholder

            try {
                tempfile.withTemporaryDirectory(tempDir => { // Create a temporary directory
                    const tempFiles = uploadedFiles.map(file => { // Loop through uploaded files
                        const tempPath = `${tempDir}/${file.name}`; // Create a temp file path
                        os.writeFileSync(tempPath, file.read()); // Save file to temp path
                        return tempPath; // Return temp file path
                    });

                    const vectorsDf = processDocuments(tempFiles, { // Process the documents
                        progressCallback: x => progressBar.progress(x), // Update progress bar
                        statusCallback: x => statusText.write(x) // Update status text
                    });

                    vectorsDf.forEach(row => { // Loop through each processed row
                        const vector = Object.values(row).slice(1); // Extract vector data
                        const metadata = { // Create metadata
                            uploaded_by: st.sessionState['companyLicense'], // Add license info
                            filename: row.filename // Add file name
                        };
                        storeVector(row.filename, vector, metadata, st.sessionState['companyLicense']); // Store vector in database
                    });

                    col1.downloadButton("Download CSV", vectorsDf.toCsv(), "document_vectors.csv"); // Button to download CSV file

                    col2.downloadButton("Download NPY", np.save("vectors.npy", vectorsDf), "vectors.npy"); // Button to download NPY file

                    st.subheader("Preview of vectorized data:"); // Display subheader for preview
                    st.dataframe(vectorsDf.head()); // Show a preview of the data
                });
            } catch (e) {
                st.error(`An error occurred during processing: ${e}`); // Show error message
            } finally {
                progressBar.empty(); // Clear progress bar
            }
        }
    }

    st.expander("\u2139\uFE0F Instructions").write(` // Expandable section for instructions
        1. Upload one or more documents using the file uploader above
        2. Click 'Process Documents' to start vectorization
        3. Wait for processing to complete
        4. Download the resulting CSV or NPY file

        Supported file formats: TXT, PDF, DOC, DOCX

        Note: The NPY file will automatically rotate when it reaches 20MB
    `); // Instructions for using the app
}

main(); // Run the main function
