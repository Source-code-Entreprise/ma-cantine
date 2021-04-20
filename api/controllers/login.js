const { saveTokenForUser, getUserForLoginToken } = require("../infrastructure/repositories/login-token");
const { findUser } = require('../infrastructure/repositories/user');
const { sendSignUpLink } = require('./sign-up');
const crypto = require('crypto');
const jwt = require("jsonwebtoken");
const { sendEmail } = require("./utils");
require('dotenv').config();

function generateToken() {
  return crypto.randomBytes(256).toString('base64');
};

function sendLoginLink(email, token) {
  // TODO: better way of generating html string (ejs.renderFile ?)
  const htmlBody = "<!DOCTYPE html> <html> <body>"+
                   "<a href='?token="+encodeURIComponent(token)+">Connectez-moi</a>"+
                   "</body> </html>";

  sendEmail([{ email }], "Votre lien de connexion avec ma cantine", htmlBody)
};

async function initiateMagicLinkLogin(email) {
  let user = await findUser({ email: email });
  if(user) {
    const token = generateToken();
    // wait to make sure token is saved successfully before it is sent
    await saveTokenForUser(user, token);
    sendLoginLink(email, token);
  } else {
    sendSignUpLink(email);
    return;
  }
};

async function generateJWTokenForUser(loginTokenString) {
  let user = await getUserForLoginToken(loginTokenString);
  if(user) {
    return jwt.sign({ email: user.email }, process.env.JWT_SECRET_KEY, { expiresIn: '7 days' });
  }
};

module.exports = {
  initiateMagicLinkLogin,
  generateJWTokenForUser
};