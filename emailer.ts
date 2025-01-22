import nodemailer from "nodemailer";  // Import the nodemailer library to send emails


// Check if necessary email settings are present in environment variables
if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD) {
  // If EMAIL_USER or EMAIL_PASSWORD are missing, throw an error
  throw new Error("Missing email configuration");
}

try {
  // Create an email transporter using Gmail
  const transporter = nodemailer.createTransport({
    service: "gmail",  // Use Gmail as the email service
    auth: {
      user: process.env.EMAIL_USER,  // Authenticate using EMAIL_USER from environment
      pass: process.env.EMAIL_PASSWORD,  // Use EMAIL_PASSWORD from environment for password
    },
  });

  // This is an asynchronous function to send a password reset email to a user
  export async function sendPasswordResetEmail(email: string, resetToken: string) {
    // Generate the URL that the user will click to reset their password
    const resetUrl = `${process.env.APP_URL}/reset-password?token=${resetToken}`;

    // Define the email details such as sender, receiver, subject, and content
    const mailOptions = {
      from: process.env.EMAIL_USER,  // Sender's email (from where the email is sent)
      to: email,  // Recipient's email address
      subject: "Password Reset Request",  // The subject of the email
      html: `
      <h1>Password Reset Request</h1>
      <p>Click the link below to reset your password:</p>
      <a href="${resetUrl}">Reset Password</a>
      <p>If you didn't request this, please ignore this email.</p>
    `,
    };

    // Send the email using the previously defined transporter and mailOptions
    await transporter.sendMail(mailOptions);
  }

} catch (error) {
  // If any error occurs during the setup or sending email, catch it here
  console.error('Failed to configure transporter or send email:', error);  // Log the error to the console
  throw new Error('Failed to send password reset email');  // Rethrow a more specific error message
}```
