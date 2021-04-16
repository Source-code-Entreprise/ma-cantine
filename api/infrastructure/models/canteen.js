// For some reason, removing the unused Sequelize from here causes the tests to break
const { Sequelize, DataTypes } = require('sequelize');
const { sequelize } = require('../postgres-database');

exports.Canteen = sequelize.define('Canteen', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    unique: true,
    autoIncrement: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  // TODO: validate city and sector input
  city: {
    type: DataTypes.STRING,
    allowNull: false
  },
  sector: {
    type: DataTypes.STRING,
    allowNull: false
  }
});
