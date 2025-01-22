import nodemailer from "nodemailer";

// Validate environment variables
if (!process.env.EMAIL_USER || !process.env.EMAIL_PASSWORD || !process.env.APP_URL) {
  throw new Error("Missing necessary environment variables for email configuration");
}

// Configure the transporter outside of the try-catch to initialize on server start
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASSWORD,
  },
});

// Function to send password reset email
export async function sendPasswordResetEmail(email: string, resetToken: string) {
  if (!email || !resetToken) {
    throw new Error("Email and reset token are required");
  }

  const resetUrl = `${process.env.APP_URL}/reset-password?token=${resetToken}`;
  const mailOptions = {
    from: `"Support" <${process.env.EMAIL_USER}>`,
    to: email,
    subject: "Password Reset Request",
    html: `
      <h1>Password Reset Request</h1>
      <p>Click the link below to reset your password:</p>
      <a href="${resetUrl}">Reset Password</a>
      <p>If you didn't request this, please ignore this email.</p>
    `,
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log(`Password reset email sent to ${email}`);
  } catch (error) {
    console.error(`Failed to send email to ${email}:`, error);
    throw new Error("Error sending password reset email");
  }
}
