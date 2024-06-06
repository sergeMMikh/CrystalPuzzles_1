const path = require('path');
const { create } = require('sass-alias');

module.exports = {
	webpack: {
		alias: {
			'@src': path.resolve(__dirname, 'src'),
			'@app': path.resolve(__dirname, 'src/app'),
			'@pages': path.resolve(__dirname, 'src/pages'),
			'@widgets': path.resolve(__dirname, 'src/widgets'),
			'@features': path.resolve(__dirname, 'src/features'),
			'@entities': path.resolve(__dirname, 'src/entities'),
			'@shared': path.resolve(__dirname, 'src/shared'),
			'@check.in': path.resolve(__dirname, 'src/pages/check.in'),
			'@supervisor': path.resolve(__dirname, 'src/pages/supervisor'),
			'@trainer': path.resolve(__dirname, 'src/pages/trainer'),
			'@student': path.resolve(__dirname, 'src/pages/student')
		},
		module: {
			rules: [
				{
					test: /^.*\.(sass|scss)$/,
					use: [
						{
							loader: 'sass-loader',
							options: {
								sassOptions: {
									importer: create({
										styles: path.join(__dirname, 'src/app/styles')
									})
								}
							}
						}
					]
				}
			]
		}
	}
};
