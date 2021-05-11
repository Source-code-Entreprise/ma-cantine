const { getDiagnosticsByCanteenHandler } = require('../../../application/routes/get-diagnostics-by-canteen');
const { hFake } = require('../../test-helper');

jest.mock("../../../domain/usecases/get-diagnostics-by-canteen");
const { getDiagnosticsByCanteen } = require("../../../domain/usecases/get-diagnostics-by-canteen");

describe('Get diagnostics by canteen handler', () => {
  it('calls usecase with connected user\'s canteen id and returns usecase result in response', async () => {
    getDiagnosticsByCanteen.mockReturnValue([{ year: 2030, valueBio: 20 }]);
    const response = await getDiagnosticsByCanteenHandler({
      auth: {
        credentials: {
          user: {
            email: "test@example.com",
            canteenId: 5
          }
        }
      }
    }, hFake);

    expect(getDiagnosticsByCanteen).toHaveBeenCalledWith(5);
    expect(getDiagnosticsByCanteen).toHaveBeenCalledTimes(1);
    expect(response.statusCode).toBe(200);
    expect(response.result).toStrictEqual([{ year: 2030, valueBio: 20 }]);
  });
});